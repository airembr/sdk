# AiRembr SDK Documentation

## Overview

**AiRembr SDK** is a software development kit that enables developers to easily store, retrieve, and manage data within the **AiRembr memory system** — a distributed infrastructure for building **AI Based Systems**.
It provides a seamless interface for integrating AiRembr’s real-time memory into any application, allowing AI agents, enterprise systems, and intelligent apps to **capture observations, query contextual memories, and evolve knowledge structures** with minimal latency.

---

## What is AiRembr?

**AiRembr** is a **neuroplastic, neurosymbolic distributed memory system** designed for real-time AI agents. It captures, synthesizes, and evolves data, enabling large language models to access stored information.
It can store both **semantic** and **knowledge-graph-like** data. By applying background processes such as **entity extraction and identification**, AiRembr can further decompose and structure stored facts.

Currently, these processes must be implemented by the developer using the SDK. AiRembr is designed to be **open and extensible** — we do not limit how you process data or extract knowledge.
Future versions will introduce optional built-in background processes, but you’ll always be free to use your own implementations.

The vision behind AiRembr is to provide a **framework for anyone to build their own AI memory infrastructure**.

---

## ✨ Key Features

* **Open Interface** – Build modern AI Memory systems, independent of any LLM or architecture
* **Real-Time Processing** – Sub-20ms latency with horizontally scalable distributed services
* **Neuroplastic Design** – Memories that continuously learn and restructure themselves
* **API-First Architecture** – Seamless integration into existing infrastructures
* **Enterprise-Grade** – Built for production-scale workloads
* **Neurosymbolic Approach** – Combines machine learning with symbolic reasoning for knowledge mining

---

## 🧩 Use Cases

* AI agents with persistent memory
* Customer data and personalization platforms
* Healthcare or enterprise knowledge systems
* Conversational AI with contextual recall
* Intelligent assistants with memory continuity

---

## ⚙️ Installation

### Prerequisites

AiRembr requires both the **service infrastructure** and the **SDK library**.

---

### Install AiRembr Service

1. Get the `docker-compose.yml` file (`wget https://raw.githubusercontent.com/airembr/sdk/master/docker-compose.yaml`)
2. Run the service:

```bash
docker compose up
```

The service will be available at:

```
http://localhost:14002
```

---

### Install AiRembr SDK

```bash
pip install airembr-sdk
```

---

## 🚀 Quick Start

> **Note:** Currently, AiRembr supports **conversation-scoped memory**, but all stored facts are retained for future processing and retrieval.

### 1. Initialize the Client

```python
from airembr_sdk.client.airembr_chat import AiRembrChatClient, entity, event

client = AiRembrChatClient(api="http://localhost:4002")

# Define entities
person = entity("person", traits={"name": "John"}, label="John Smith", id="1")
agent = entity("agent", traits={"name": "ChatGPT"}, id="3")
message = entity("message", traits={"type": "chat"}, id="2")

# Define observation
observation = (
    client.
    observation(
        source_id="123",
        id="o1",
        label="messaged",
        observer=person,
        description="Describe the observation in plain text")
    .context({person, agent, message})  # Connected entities
)

observation.remember()
```

---

## 🧠 Core Concepts

### Observations

Observations are the **fundamental data units** in AiRembr. Each observation contains:

* **Actor** – The entity performing the action (e.g., person or agent)
* **Event** – The type of action (e.g., "message")
* **Objects** – Data associated with the event

Actors and objects are treated as **entities** that can be identified and merged. Over time, repeated interactions enrich entities with additional traits and relationships.

---

### Conversation Memory vs. Long-Term Memory

| Type                    | Description                                                                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Conversation Memory** | Stores and retrieves messages within a specific chat session. Provides contextual recall and automatic compression when limits are reached. Indexed by `chat_id`. |
| **Long-Term Memory**    | (Coming Soon) Enables cross-session memory retrieval and semantic search across historical data. Currently requires a custom implementation.                      |

---

### Extensibility

AiRembr is designed to be **your experimental memory foundry** — a sandbox for developing different approaches to AI memory systems.
Future versions will include built-in long-term retrieval APIs, but the current release empowers developers to build their own.

---

## 🗺️ Roadmap

Planned features for upcoming releases:

* Built-in long-term memory retrieval across sessions
* Internal reasoning and reflection mechanisms
* Memory model training capabilities
* Pre-built retrieval and embedding add-ons
* Semantic and hybrid search integrations

---

## 📜 SDK License

AGPL License © 2026 AiRembr

