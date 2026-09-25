# MEMORA

**Memory Network & Reconstruction Engine**

MEMORA is a lightweight, local-first memory engine for conversations and knowledge. It models information as a compact graph of messages, concepts, contexts, and relations so useful context can be retrieved and reconstructed without a heavyweight AI stack.

## Core principle

> Store the minimum useful representation that allows information to be connected, retrieved, explained, and reconstructed.

The first version uses Python + SQLite, compressed message payloads, deterministic indexing, and graph-aware retrieval. Embeddings and LLMs are optional future layers.

## First product milestone

- Conversation/message ingestion.
- Compact persistent SQLite storage.
- Message, chat, concept, and relation nodes.
- SQLite FTS5 retrieval.
- Graph-aware recall.
- Traceable context reconstruction.
- JSON output for agents and future UIs.
- Automated tests.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
memora init memory.db
memora add-chat memory.db "Proyecto MEMORA"
memora add-message memory.db 1 user "Estamos diseñando una nube de memoria conectada."
memora recall memory.db "memoria conectada"
python -m pytest
```

## Roadmap

**M0:** storage + graph + retrieval + reconstruction — current target.

**M1:** consolidation, temporal relations, deduplication and better concept extraction.

**M2:** optional embeddings and hybrid retrieval.

**M3:** self-description and memory-health metrics.

**M4:** graph/search interface.

**M5:** LLM adapters and agent memory protocol.
