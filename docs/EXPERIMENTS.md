# MEMORA — Experiments and Validation

**Started:** 2026-09-25

This document defines the first reproducible validation battery for the core hypothesis of MEMORA: a compact graph representation can preserve enough structure to recover useful context without copying complete conversation histories into every context.

## Baseline measurements

Every experiment should record:

- number of source messages;
- UTF-8 bytes of source messages;
- SQLite file bytes;
- number of nodes by kind;
- number of edges;
- number of unique terms;
- lexical retrieval hits;
- reconstruction nodes;
- cross-chat retrieval hits;
- duplicate rate;
- storage bytes per source byte;
- concept/message ratio;
- edge/message ratio;
- false/noisy context observed during manual evaluation.

The measurements are descriptive. They are not evidence of a general compression law.

## Required regression scenarios

### R1 — Basic persistence

Create a chat, add messages, close the database, reopen it, and verify that messages and relationships remain available.

### R2 — Deduplication

Insert identical message content twice and verify that the node representation is reused.

### R3 — Cross-chat connection

Place related information in two different chats. A query should be able to retrieve evidence from both when the graph connects them through shared structure.

### R4 — Reconstruction traceability

Every reconstructed item must identify its node ID and kind so a future interface can explain why the item entered the context.

### R5 — Compactness

Compare repeated source content against the number of unique stored message/concept nodes. Do not call the result "sublinear" unless the experiment actually measures scaling across increasing input sizes.

## Acceptance rule

A new memory mechanism is accepted only when it improves at least one measured capability without causing an unacceptable regression in retrieval precision, traceability, stability, or storage growth.

The experiment suite is part of the product, not an afterthought: MEMORA must be able to demonstrate what it remembers and why.

## Scaling benchmark

The first scaling harness is `experiments/benchmark.py`. It generates controlled Spanish conversation fragments with:

- repeated bridge vocabulary, which should become shared concept nodes;
- unique fragment identifiers, which should remain terms rather than concept nodes;
- messages distributed across multiple chats.

Run the standard scaling battery:

```powershell
python -m experiments.benchmark --sizes 10 100 1000 5000 10000 --chats 10
```

For a smaller smoke run:

```powershell
python -m experiments.benchmark
```

The benchmark reports source UTF-8 bytes, normalized SQLite bytes, storage/source ratio, node/edge counts, edge/message ratio, unique terms, a counterfactual naive-concept proxy, concept/message ratio, concepts per 100 messages, estimated concept reduction against that proxy, lexical hits, reconstruction size, cross-chat coverage, and duplicate rate.

The naive concept count is explicitly a **counterfactual proxy**, not a historical reimplementation of every detail of the earliest MVP. It asks: "How many concept nodes would exist if every unique indexed term were materialized?" This makes the effect of concept promotion measurable without requiring two production policies to coexist.

SQLite is checkpointed before the database-size measurement so the WAL is not silently excluded from the reported persistent footprint. The benchmark is intentionally descriptive: storage growth, ratios, and retrieval coverage are observations, not a proof of sublinear scaling.

The small benchmark is also a regression test. Large sizes remain opt-in so CI stays deterministic and inexpensive.
