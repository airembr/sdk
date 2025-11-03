# AiRembr SDK Documentation

## Overview

**AiRembr SDK** is a software development kit that enables developers to easily store, retrieve, and manage data within the **AiRembr memory system** — a distributed infrastructure for building **AI Memory Systems**.
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

1. Clone the repository and get the `docker-compose.yml` file
2. Run the service:

```bash
docker compose up
```

The service will be available at:

```
http://localhost:4002
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
from sdk.airembr.client import AiRembrChatClient

client = AiRembrChatClient(
    api="http://localhost:4002",
    source_id="8351737-a9ad-4c29-a01b-2f3180bec592",
    person_instance="person #1",
    person_traits={"name": "Adam", "surname": "Nowak"},
    agent_traits={"name": "ChatGPT", "model": "openai-5"},
    chat_id="chat-1"
)
```

### 2. Send Messages

```python
# Person sends a message. This should be somewhere in your chat code. It does not query LLM just saves the message.
client.chat("Hi, how are you?", "person")

# Agent responds
client.chat("I'm fine.", "agent")
```

### 3. Retrieve Conversation Memory

```python
# Save Facts (messages)  and retrieve conversation memory for this chat
memory = client.remember(realtime='collect,store,destination')
```

> The `remember()` method retrieves **conversation memory** for the specific `chat_id`.
> It includes messages, summaries, entities, and contextual metadata — all compressed and indexed for low-latency recall.

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

### Memory Structure

Each retrieved conversation memory includes:

* **Summary** – Compressed representation of previous chat context
* **Entities** – Identified actors with their traits
* **Messages** – Recent conversation history
* **Context** – Temporal and environmental metadata

#### Example Response

```python
{
    "chat-1": """
        Summary of previous chat:
        Adam and the agent discussed LLM history...

        Entities:
          person -> (name: Adam, surname: Nowak)
          agent -> (name: ChatGPT, model: openai-5)

        Current messages:
          [date] person: Hi, how are you?
          [date] agent: I’m fine.

        Context:
          Now: 2025-11-03 09:39:23 (Monday)
    """
}
```

---

## 🧰 API Reference

### `AiRembrChatClient`

#### Constructor Parameters

| Parameter         | Type   | Required | Description                                    |
| ----------------- | ------ | -------- | ---------------------------------------------- |
| `api`             | `str`  | ✅        | AiRembr service endpoint URL                   |
| `source_id`       | `str`  | ✅        | Unique identifier for the data source          |
| `person_instance` | `str`  | ✅        | Identifier for the person instance  (entity #ID)           |
| `person_traits`   | `dict` | ✅        | Attributes of the person (e.g., name, email)   |
| `agent_traits`    | `dict` | ✅        | Attributes of the agent (e.g., model, version) |
| `chat_id`         | `str`  | ✅        | Unique identifier for the conversation         |

---

#### `chat(message, actor)`

Sends a message to the AiRembr system and stores it as an observation.

```python
client.chat("Hello!", "person")
```

**Parameters**

* `message` *(str)* – Message text
* `actor` *(str)* – `"person"` or `"agent"`

---

#### `remember(realtime)`

Retrieves the stored conversation memory for the active chat session.

```python
memory = client.remember(realtime='collect,store,destination')
```

**Parameters**

* `realtime` *(str)* – Specifies which parts of the ingestion pipeline run in real time

**Returns**

* A dictionary containing memories indexed by `chat_id`

---

## ⚡ Features

* **Automatic Context Compression** – Keeps context within window limits while maintaining continuity
* **Multi-Chat Support** – Each `chat_id` maintains its own memory scope
* **Entity Tracking** – Identifies and merges entities automatically, evolving over time

---

## 🧩 Advanced Usage

### Building Long-Term Memory Systems

To extend AiRembr beyond conversation-scoped memory:

1. **Build a Retrieval System**

   * Query stored data across sessions
   * Use vector or symbolic search

2. **Implement an Embedding Pipeline**
   * Process incoming facts and store embeddings in a database

3. **Design a Retrieval Strategy**

   * Combine symbolic and semantic search methods

> AiRembr provides the **infrastructure foundation** — you control how long-term memory and retrieval logic evolve.

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

MIT License © 2025 AiRembr

