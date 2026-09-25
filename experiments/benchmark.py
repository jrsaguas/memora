from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from memora.core import Memora


BRIDGE_TERMS = (
    "memoria contexto reconstruccion conexion",
    "grafo memoria contexto",
    "reconstruccion informacion entre conversaciones",
)


def synthetic_message(index: int, chat_index: int) -> str:
    bridge = BRIDGE_TERMS[index % len(BRIDGE_TERMS)]
    unique = f"fragmento{index:06d} chat{chat_index:03d}"
    return (
        f"{bridge}. "
        f"Este fragmento documenta una decision tecnica sobre MEMORA. "
        f"{unique} conserva evidencia y permite recuperar relaciones."
    )


def source_bytes(messages: list[str]) -> int:
    return sum(len(message.encode("utf-8")) for message in messages)


def measure(size: int, chats: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="memora-benchmark-") as tmp:
        path = Path(tmp) / "memory.db"
        m = Memora(path)
        chat_ids = [m.add_chat(f"Chat {i}") for i in range(chats)]
        messages: list[str] = []

        for i in range(size):
            chat_index = i % chats
            content = synthetic_message(i, chat_index)
            messages.append(content)
            m.add_message(chat_ids[chat_index], "user", content)

        # Normalize WAL footprint before measuring persistent storage.
        m.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        m.db.commit()

        stats = m.stats()
        unique_terms = int(
            m.db.execute("SELECT COUNT(DISTINCT term) FROM terms").fetchone()[0]
        )
        cross_chat = m.recall(
            "memoria contexto reconstruccion",
            limit=min(20, max(4, size)),
            depth=1,
        )
        hit_chat_ids = {
            item["chat_id"]
            for item in cross_chat["reconstruction"]
            if item["kind"] == "message" and item["chat_id"] is not None
        }
        concept_nodes = stats["nodes"].get("concept", 0)
        message_nodes = stats["nodes"].get("message", 0)

        result = {
            "messages": size,
            "chats": chats,
            "source_utf8_bytes": source_bytes(messages),
            "database_bytes": stats["database_bytes"],
            "nodes": stats["nodes"],
            "edges": stats["edges"],
            "unique_terms": unique_terms,
            "concept_to_message_ratio": (
                concept_nodes / message_nodes if message_nodes else 0.0
            ),
            "lexical_hits": len(cross_chat["matches"]),
            "reconstruction_nodes": len(cross_chat["reconstruction"]),
            "cross_chat_hits": len(hit_chat_ids),
        }
        m.close()
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="MEMORA compactness/scaling benchmark")
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[10, 100, 1000],
        help="message counts to benchmark",
    )
    parser.add_argument("--chats", type=int, default=5)
    args = parser.parse_args()

    if args.chats < 1 or any(size < 1 for size in args.sizes):
        parser.error("sizes and chats must be positive")

    results = [measure(size, args.chats) for size in args.sizes]
    print(json.dumps({"benchmark": "concept-promotion-scaling", "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
