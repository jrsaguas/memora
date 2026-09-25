from __future__ import annotations
import argparse
import json
from .core import Memora

def parser():
    p = argparse.ArgumentParser(prog="memora")
    s = p.add_subparsers(dest="command", required=True)
    for name in ("init","stats","export"):
        x = s.add_parser(name); x.add_argument("db")
    x = s.add_parser("add-chat"); x.add_argument("db"); x.add_argument("title")
    x = s.add_parser("add-message"); x.add_argument("db"); x.add_argument("chat_id", type=int); x.add_argument("role"); x.add_argument("content")
    x = s.add_parser("search"); x.add_argument("db"); x.add_argument("query"); x.add_argument("--limit", type=int, default=10)
    x = s.add_parser("recall"); x.add_argument("db"); x.add_argument("query"); x.add_argument("--limit", type=int, default=8); x.add_argument("--depth", type=int, default=1)
    return p

def main():
    a = parser().parse_args()
    m = Memora(getattr(a, "db", ":memory:"))
    try:
        if a.command == "init": print(json.dumps({"database":a.db,"status":"ready"}))
        elif a.command == "add-chat": print(m.add_chat(a.title))
        elif a.command == "add-message": print(m.add_message(a.chat_id,a.role,a.content))
        elif a.command == "search": print(json.dumps([x.__dict__ for x in m.search(a.query,a.limit)],ensure_ascii=False,indent=2))
        elif a.command == "recall": print(json.dumps(m.recall(a.query,a.limit,a.depth),ensure_ascii=False,indent=2))
        elif a.command == "stats": print(json.dumps(m.stats(),ensure_ascii=False,indent=2))
        elif a.command == "export": print(m.export_json())
    finally:
        m.close()

if __name__ == "__main__":
    main()
