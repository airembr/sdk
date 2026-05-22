# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Install dependencies
```bash
pip install -r requirements.txt
# For the public SDK only:
pip install airembr_sdk/requirements.txt
```

## Architecture

There are **two separate Python packages** in this repo with distinct roles:

### `airembr_sdk/` — Public SDK (published to PyPI as `airembr-sdk`)
Minimal dependencies (`requests`, `pydantic`). This is the external developer-facing library.

- `client/airembr_api.py` — `AirembrApi`: low-level HTTP transport to the collector API
- `client/airembr_chat.py` — `AiRembrChatClient` + `AirembrObservation` + `AirembrChat`: fluent API for building and sending observations and chat sessions
- `client/airembr_query.py` — `AirembrClient`: higher-level client wrapping observation submission and query methods
- `model/interface/` — Pydantic models for the wire format: `IObservation`, `IObservationEntity`, `IObservationRelation`, `IConversationMemory`, etc.
- `model/core/instance.py` — `Instance`: custom `str` subtype that encodes entity references as `*kind:role#id`. Entity IDs can be static, reference-resolved (`$field`), or hashed (`.#` suffix).
- `model/core/instance_link.py` — `InstanceLink`: named reference handle used to wire entities together in an observation before sending.

### `airembr/` — Internal library (server-side and heavy infrastructure)
Used by server processes, workers, and internal tooling. Heavy dependencies.

- `core/` — Utility modules: hashing, time parsing, text processing, security, env validation, etc.
- `model/` — Shared data models used by both public SDK and server side: `bigdata/` flat DB row models, `metadata/` system configuration models, `api/` request/response models, `system/` domain models
- `protocol/` — Abstract protocols for Redis cache operations
- `adapter/qdrant/` — Qdrant vector DB adapter
- `db/` — Static lookup data (aspects, languages, social media domains, etc.)
- `sdk/ai/` — AI processing: entity extraction prompts, entity taxonomy (loaded from `taxonomy.json`), LLM adapter (`LLMAdapter`) with driver support for OpenRouter, OpenAI, Anthropic, Google
- `sdk/service/parser/tql/` — TQL (Tracardi Query Language): Lark-based grammar and transformer that compiles filter expressions to SQL
- `sdk/service/parser/eql/` — EQL (Entity Query Language): Lark-based grammar for entity queries
- `sdk/service/remote/llm/` — `LLMAdapter` unified interface over multiple LLM providers (async `infer()` with optional structured output via Pydantic)
- `sdk/storage/` — Storage adapters: Redis cache layers, SQLite/MySQL metadata via SQLAlchemy, LanceDB vector store
- `system/process/` — Background workers: observation collection pipeline, destination dispatching, embedding workers, conversation memory (Redis-backed)
- `system/process/ai/memory/conversation/` — Conversation memory: `memorizer` context manager that loads/saves messages and triggers summarization via LLM when limits are reached

## Infrastructure

The service stack runs via Docker Compose:
- **GUI** — `http://localhost:14000`
- **GUI API** — `http://localhost:14001`
- **Collector API** (observation ingestion endpoint) — `http://localhost:14002`
- **Redis** — `localhost:6379` (conversation memory)
- **StarRocks** — `localhost:9030/8030/8040` (analytical/big-data storage)

## Key design patterns

**Observation model**: an `IObservation` contains a map of `InstanceLink → IObservationEntity` plus a list of `IObservationRelation`. Relations reference entities by `InstanceLink`, not by embedding them. Entities carry an `Instance` string (e.g., `person #email@example.com`) which encodes type, optional role, and optional ID. Use `Instance.type(type, id)` as the factory.
**LLM configuration**: provider and model selection live in `airembr/sdk/ai/config.py`, driven by env vars `OPENROUTER_API_KEY`, `EMBEDDING_HOST`, `EMBEDDING_API_KEY`. The file contains commented-out model alternatives reflecting experimentation history — the last assignment wins.
