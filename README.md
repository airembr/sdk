# AiRembr - AI memory that can explain itself.

AiRembr is open-source, self-hosted memory infrastructure for AI applications. It turns documents, emails, APIs and conversations into a deterministic, structured semantic index — one where every fact traces back to the observation that produced it, every answer is reproducible, and everything runs on infrastructure you own.

Instead of a single opaque `mem.add()` / `mem.search()` API bolted onto a vector store, AiRembr gives you a composable pipeline you configure: raw signals in, structured knowledge out.

## The problem

Most AI initiatives don't fail on the model — they fail on the data underneath it. Knowledge is scattered across silos that don't agree with each other, most agent pilots never reach production, and the memory frameworks available today store raw text and embeddings with no way to explain *why* an answer came back, whether it's still true, or where it came from.

## How it works

Four steps take raw signals to structured, queryable memory:

1. **Observe** — Documents, emails, APIs and conversations stream in as observations. Nothing to model up front.
2. **Understand** — Entities, events and relations are extracted and resolved (the email sender "ACME" becomes the customer "ACME").
3. **Index** — Facts land in a versioned semantic index — compressed, deduplicated, and enriched by event-driven rules as new data arrives.
4. **Retrieve** — Apps, agents and analysts query the same index. Deterministic answers, with AI reasoning invoked only on demand.

Underneath, the pipeline is built from small, typed, composable stages you assemble yourself:

- **Capture** — Observation, Entity, Fact
- **Enhance** — Extract Facts, Infer Implicit Facts, Orchestrate & Trigger
- **Use** — Retrieval, Reasoning, Forgetting

## Two calls: observe, then search

```python
from airembr_sdk.client.airembr_chat import AiRembrChatClient, entity

client = AiRembrChatClient(api="http://localhost:8686")

person = entity("person", traits={"name": "John"}, label="John Smith", id="1")
agent  = entity("agent",  traits={"name": "ChatGPT"}, id="3")

(
    client
    .observation(source_id="123", id="o1", label="messaged",
                 observer=person, description="Describe the observation in plain text")
    .context({person, agent})
    .remember()
)
```

```python
facts = client.search("open invoices for ACME", scope="facts")

for f in facts:
    print(f.entity, f.value, f.source)
```

## Why AiRembr

| Others | AiRembr |
|---|---|
| Stores raw text and embeddings | Stores structured entities, facts and relations |
| Answers drift between runs | Deterministic, reproducible retrieval |
| Black-box similarity scores | Explainable results with provenance |
| Memory locked to a single app | One index shared by every app and agent |
| Grows into an unsearchable pile | Compresses and forgets by rule |
| An LLM in the loop of every lookup | AI only when reasoning is needed |
| Self-hosting deprecated or feature-gated | Open source, self-hosted, nothing withheld |
| Poisoned or stale memories persist silently | Versioned facts, conflict-aware, forgetting by rule |

Core traits: **Observable** (every fact traces to its source), **Versioned** (ask what was true last quarter, not just today), **Deterministic** (same query, same answer), **Secure** (scoped access, encryption, audit trails), **Self-hosted**, **Composable**, **Extensible** (custom extractors, rules, storage backends), **Distributed** (scales horizontally across nodes and regions).

## Who it's for

- **AI agencies & system integrators** — build the memory practice once, configure it per client, and hand over something the client can actually audit and maintain instead of walking away from a bespoke one-off.
- **AI builders & indie/startup teams** — a memory framework you grow into, not out of: no metered credits, no feature-gated tiers, no self-hosting rug-pull.
- **Enterprises entering the AI era** — a governed, explainable memory substrate that breaks down data silos without giving up control, with provenance and audit trails as the foundation rather than a compliance afterthought.
