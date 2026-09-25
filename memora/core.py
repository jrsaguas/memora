from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import zlib
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[\wÀ-ÿ]{3,}", re.UNICODE)

@dataclass(frozen=True)
class Memory:
    id: int
    kind: str
    content: str
    chat_id: int | None
    created_at: str

class Memora:
    """Local-first memory graph backed by one SQLite database."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self._schema()

    def close(self):
        self.db.close()

    def _schema(self):
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS nodes(
            id INTEGER PRIMARY KEY,
            kind TEXT NOT NULL,
            external_id TEXT,
            title TEXT,
            payload BLOB,
            content_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS edges(
            source_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
            target_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
            relation TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            PRIMARY KEY(source_id,target_id,relation)
        );
        CREATE TABLE IF NOT EXISTS terms(
            node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
            term TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            PRIMARY KEY(node_id,term)
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS node_fts USING fts5(title,text,node_id UNINDEXED);
        CREATE INDEX IF NOT EXISTS idx_nodes_kind ON nodes(kind);
        CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
        CREATE INDEX IF NOT EXISTS idx_terms_term ON terms(term);
        """)
        self.db.commit()

    @staticmethod
    def _hash(kind, content, title=""):
        return hashlib.sha256(f"{kind}\0{title}\0{content}".encode()).hexdigest()

    @staticmethod
    def _terms(text):
        return sorted(set(t.lower() for t in TOKEN_RE.findall(text)))

    def _node(self, kind, content, title="", external_id=None):
        digest = self._hash(kind, content, title)
        row = self.db.execute("SELECT id FROM nodes WHERE content_hash=?", (digest,)).fetchone()
        if row:
            return int(row["id"])
        payload = zlib.compress(content.encode("utf-8"), 9)
        cur = self.db.execute(
            "INSERT INTO nodes(kind,external_id,title,payload,content_hash) VALUES(?,?,?,?,?)",
            (kind, external_id, title, payload, digest),
        )
        node_id = int(cur.lastrowid)
        terms = self._terms(f"{title} {content}")
        self.db.executemany(
            "INSERT OR IGNORE INTO terms(node_id,term) VALUES(?,?)",
            [(node_id, term) for term in terms],
        )
        self.db.execute(
            "INSERT INTO node_fts(title,text,node_id) VALUES(?,?,?)",
            (title, " ".join(terms), str(node_id)),
        )
        self.db.commit()
        return node_id

    def add_chat(self, title, external_id=None):
        return self._node("chat", "", title, external_id)

    def add_message(self, chat_id, role, content, external_id=None):
        node_id = self._node("message", content, role, external_id)
        self.link(node_id, chat_id, "belongs_to")
        for term in self._terms(content):
            concept = self._node("concept", term, term)
            self.link(node_id, concept, "mentions")
        return node_id

    def link(self, source_id, target_id, relation, weight=1.0):
        self.db.execute(
            "INSERT OR REPLACE INTO edges(source_id,target_id,relation,weight) VALUES(?,?,?,?)",
            (source_id,target_id,relation,weight),
        )
        self.db.commit()

    def _content(self, row):
        return zlib.decompress(row["payload"]).decode("utf-8") if row["payload"] else ""

    def _chat_for(self, node_id):
        row = self.db.execute(
            "SELECT target_id FROM edges WHERE source_id=? AND relation='belongs_to'",
            (node_id,),
        ).fetchone()
        return int(row["target_id"]) if row else None

    def get(self, node_id):
        row = self.db.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
        if not row:
            return None
        return Memory(int(row["id"]), row["kind"], self._content(row), self._chat_for(row["id"]), row["created_at"])

    def search(self, query, limit=10):
        terms = self._terms(query)
        if not terms:
            return []
        match = " OR ".join(f'"{t}"' for t in terms)
        rows = self.db.execute("""
            SELECT n.*, bm25(node_fts) AS rank
            FROM node_fts JOIN nodes n ON n.id=CAST(node_fts.node_id AS INTEGER)
            WHERE node_fts MATCH ? ORDER BY rank LIMIT ?
        """, (match, limit)).fetchall()
        return [Memory(int(r["id"]), r["kind"], self._content(r), self._chat_for(r["id"]), r["created_at"]) for r in rows]

    def neighbors(self, node_id, depth=1, limit=50):
        seen, frontier = {node_id}, {node_id}
        for _ in range(max(0, depth)):
            if not frontier:
                break
            marks = ",".join("?" * len(frontier))
            params = tuple(frontier) + tuple(frontier) + (limit,)
            rows = self.db.execute(
                f"SELECT source_id,target_id FROM edges WHERE source_id IN ({marks}) OR target_id IN ({marks}) LIMIT ?",
                params,
            ).fetchall()
            nxt = set()
            for r in rows:
                nxt.update((int(r["source_id"]), int(r["target_id"])))
            nxt -= seen
            seen |= nxt
            frontier = nxt
        result = []
        for nid in list(seen - {node_id})[:limit]:
            item = self.get(nid)
            if item:
                result.append(item)
        return result

    def recall(self, query, limit=8, depth=1):
        hits = self.search(query, limit)
        context, seen = [], set()
        for hit in hits:
            for item in [hit, *self.neighbors(hit.id, depth)]:
                if item.id not in seen:
                    seen.add(item.id)
                    context.append(item)
        context.sort(key=lambda x: (x.kind != "message", x.created_at, x.id))
        return {
            "query": query,
            "matches": [self._json_memory(x) for x in hits],
            "reconstruction": [self._json_memory(x) for x in context[:limit * 3]],
        }

    @staticmethod
    def _json_memory(m):
        return {"id": m.id, "kind": m.kind, "chat_id": m.chat_id, "content": m.content}

    def stats(self):
        counts = {r["kind"]: int(r["n"]) for r in self.db.execute("SELECT kind,COUNT(*) n FROM nodes GROUP BY kind")}
        edges = int(self.db.execute("SELECT COUNT(*) n FROM edges").fetchone()["n"])
        size = Path(self.path).stat().st_size if Path(self.path).exists() else 0
        return {"nodes": counts, "edges": edges, "database_bytes": size}

    def export_json(self):
        nodes = []
        for row in self.db.execute("SELECT * FROM nodes ORDER BY id"):
            nodes.append({"id":row["id"],"kind":row["kind"],"title":row["title"],"content":self._content(row),"created_at":row["created_at"]})
        edges = [dict(r) for r in self.db.execute("SELECT * FROM edges ORDER BY source_id")]
        return json.dumps({"nodes":nodes,"edges":edges}, ensure_ascii=False, indent=2)
