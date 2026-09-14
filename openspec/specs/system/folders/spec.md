# System Folders

## Purpose

Defines where to find system files and separate sub-projects.

## Description

This project consists of several subprojects, located at:

/home/risto/PycharmProjects/dev/bizmory
Deployable service layer of "Airembr", an AI memory platform: collects facts (actor-predicate-object triples) from observations into a StarRocks-backed knowledge graph, and serves retrieval via natural language / EQL queries.
- api/ : FastAPI servers — retrieval/recall API (port 7000) and enhancer/entity-enrichment API (port 8000).
- bg/  : background workers (asyncio scripts) — embedder, event-trigger dispatcher, observation merger, iCal source ingester.
Depends directly on airembr/sdk (airembr core + airembr_sdk) and on starrocks-driver (srd) for StarRocks queries.
/home/risto/WebstormProjects/console
  React 19 + Vite + MUI + Redux Toolkit GUI ("airembr-gui") — the admin/management console. Talks only over HTTP to the backend management API (bearer token + tenant/context headers); no direct code dependency on any other subproject in this system.

/home/risto/PycharmProjects/dev/airembr/dagor 
  Workflow/DAG execution engine (flows, nodes, edges, plugins). Embedded directly by airembr/sdk (imported in sdk's flow/plugin/installer/deployment modules) to run workflow-based automations; not used directly by bizmory.

/home/risto/PycharmProjects/dev/pararun
  Transport-agnostic deferred-task execution framework (Celery-like), with Kafka (default, confluent-kafka) and Pulsar adapters selected via QUEUE_ADAPTER. Used by airembr/sdk's background workers (collector/observation/fact/trigger workers) to dispatch async tasks; not used directly by bizmory.

/home/risto/PycharmProjects/dev/airembr/sdk
  Main catalog of the system ("airembr"). Contains:
  - airembr/     : core internal library (models, storage adapters, AI/LLM processing, background process logic). Embeds dagor and pararun.
  - airembr_api/ : FastAPI servers embedding airembr core directly — collector API (ingestion, port 4002) and GUI API (management backend for console, port 4001).
  - airembr_sdk/ : public SDK (PyPI: airembr-sdk), minimal deps (requests, pydantic) — HTTP client library wrapping airembr_api; imports shared models from airembr core.
  - airembr_mcp/ : MCP server exposing memory tools (remember, ask, search_observations, add_entities_to_observation) over HTTP; reaches airembr_api's collector/GUI services exclusively via airembr_sdk, never imports airembr core directly.
  - test/        : tests.
  Depends on dagor and pararun (embedded), and on starrocks-driver (srd) for big-data/StarRocks queries.

/home/risto/PycharmProjects/dev/starrocks-driver
  `srd` — async SQLAlchemy-based StarRocks driver/query-builder (StarrocksDriver, AsyncStarRocksEngine, SQL AST builder). Used by airembr/sdk's big-data adapter layer, and directly by bizmory's bg/ workers and retrieval SQL service.

## How they connect

- console --HTTP (bearer/tenant headers)--> airembr_api (gui:4001) / bizmory api (retrieval:7000, enhancer:8000)
- bizmory --imports--> airembr/sdk (airembr core + airembr_sdk), and --imports--> starrocks-driver (srd) directly for SQL (bizmory will be removed in the future after moving all API to airembr_api)
- airembr/sdk: airembr (core) <- airembr_api (in-process embed) ; airembr (core) <- airembr_sdk (client lib, shares models) <- airembr_mcp (HTTP-only client, never touches core directly)
- airembr/sdk --imports--> dagor (workflow engine) and pararun/pararun_adapter (Kafka/Pulsar task dispatch) — both embedded, not standalone services
- airembr/sdk + bizmory --imports--> starrocks-driver (srd) for StarRocks queries (shared big-data storage layer)
