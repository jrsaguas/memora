from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path

from memora.core import Memora
from experiments.benchmark import synthetic_message


def build_memory(size: int, chats: int) -> tuple[Memora, list[int]]:
    tmp = tempfile.TemporaryDirectory(prefix="memora-performance-")
    path = Path(tmp.name) / "memory.db"
    m = Memora(path)
    chat_ids = [m.add_chat(f"Chat {i}") for i in range(chats)]
    m._benchmark_tmp = tmp  # keep the directory alive until the caller closes it

    for i in range(size):
        m.add_message(
            chat_ids[i % chats],
            "user",
            synthetic_message(i, i % chats),
        )
    return m, chat_ids


def median_ms(samples: list[float]) -> float:
    return statistics.median(samples) * 1000.0


def measure(size: int, chats: int, repeats: int) -> dict:
    m, _ = build_memory(size, chats)
    query = "memoria contexto reconstruccion"

    search_samples = []
    recall_samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        m.search(query, limit=20)
        search_samples.append(time.perf_counter() - start)

        start = time.perf_counter()
        m.recall(query, limit=20, depth=1)
        recall_samples.append(time.perf_counter() - start)

    # Ingestion is measured separately so retrieval timings are not mixed with
    # database construction cost.
    m.close()
    tmp = m._benchmark_tmp
    tmp.cleanup()

    return {
        "messages": size,
        "chats": chats,
        "repeats": repeats,
        "search_median_ms": median_ms(search_samples),
        "search_p95_ms": sorted(search_samples)[max(0, int(len(search_samples) * 0.95) - 1)] * 1000.0,
        "recall_median_ms": median_ms(recall_samples),
        "recall_p95_ms": sorted(recall_samples)[max(0, int(len(recall_samples) * 0.95) - 1)] * 1000.0,
    }


def measure_ingestion(size: int, chats: int) -> float:
    tmp = tempfile.TemporaryDirectory(prefix="memora-ingestion-")
    path = Path(tmp.name) / "memory.db"
    m = Memora(path)
    chat_ids = [m.add_chat(f"Chat {i}") for i in range(chats)]

    start = time.perf_counter()
    for i in range(size):
        m.add_message(
            chat_ids[i % chats],
            "user",
            synthetic_message(i, i % chats),
        )
    elapsed = time.perf_counter() - start

    m.close()
    tmp.cleanup()
    return elapsed


def run(size: int, chats: int, repeats: int) -> dict:
    ingestion = measure_ingestion(size, chats)
    retrieval = measure(size, chats, repeats)
    retrieval["ingestion_seconds"] = ingestion
    retrieval["ingestion_ms_per_message"] = ingestion * 1000.0 / size
    return retrieval


def main() -> None:
    parser = argparse.ArgumentParser(description="MEMORA controlled timing benchmark")
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000, 5000])
    parser.add_argument("--chats", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    if args.chats < 1 or args.repeats < 1 or any(size < 1 for size in args.sizes):
        parser.error("sizes, chats and repeats must be positive")

    results = [run(size, args.chats, args.repeats) for size in args.sizes]
    print(json.dumps({
        "benchmark": "controlled-timing",
        "note": "timing is environment-dependent; compare runs on the same machine",
        "results": results,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
