<div align="center">

# ⚡ docs-retriever-mcp
### *Universal Model Context Protocol Service for Dynamic Semantic Retrieval*

[![Protocol](https://img.shields.io/badge/Protocol-MCP%20v2.0%20(Stateless)-blueviolet?style=for-the-badge)](https://modelcontextprotocol.io)
[![Transport](https://img.shields.io/badge/Transport-stdio%20(JSON--RPC)-blue?style=for-the-badge)](#)
[![Vector Engine](https://img.shields.io/badge/Engine-ChromaDB%20%2B%20Gemini-orange?style=for-the-badge)](#)
[![Portability](https://img.shields.io/badge/Verified%20Clients-LangGraph%20%7C%20Claude%20Desktop-success?style=for-the-badge)](#)

<p align="center">
  <b>A decoupled, plug-and-play documentation intelligence engine.</b><br>
  Built on the open Model Context Protocol standard to deliver instantaneous vector search across multiple AI workflows without framework lock-in or client-side database overhead.
</p>

---

</div>

## 🌐 The Problem: Monolithic Lock-In vs. Universal MCP

Traditional Retrieval-Augmented Generation (RAG) tightly couples database dependencies directly into agent application code. This architecture causes environment bloat, fragile dependencies, and forces developers to rewrite integration logic for every new AI interface.

`docs-retriever-mcp` extracts retrieval into an independent, protocol-driven microservice. Any AI client speaking the open MCP standard can discover, inspect, and invoke documentation retrieval dynamically.

```mermaid
flowchart TD
    subgraph Legacy ["❌ Legacy Approach: Tight Coupling"]
        direction TB
        AgentA["LangGraph Agent"] -->|Direct Import| DB1[("In-Memory Vector DB")]
        DesktopA["Desktop AI"] -->|Custom Adapter| DB2[("Duplicate Vector DB")]
    end

    subgraph Modern ["✅ Modern Architecture: Protocol Decoupling"]
        direction TB
        Client1["LangGraph Pipeline"] -->|Standard JSON-RPC| MCP["docs-retriever-mcp"]
        Client2["Claude Desktop"] -->|Standard JSON-RPC| MCP
        MCP -->|Unified Search| ChromaStore[("ChromaDB Vector Store")]
    end

    style Legacy fill:#fff1f0,stroke:#ffa39e,stroke-width:1px
    style Modern fill:#f6ffed,stroke:#b7eb8f,stroke-width:1px
    style MCP fill:#e6f7ff,stroke:#91d5ff,stroke-width:2px

```

---

## 🏛️ System Architecture & Data Flow

The server operates over standard I/O (`stdio`), acting as an on-demand process managed directly by client applications. There are zero open network ports, zero firewall hurdles, and zero authentication servers required for local execution.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Prompt
    participant Client as MCP Client (Claude Desktop / LangGraph)
    participant Server as docs-retriever-mcp (stdio Subprocess)
    participant Embedder as Embedding Model (3,072-dim)
    participant Store as Local ChromaDB

    User->>Client: "How are background tasks configured?"
    Note over Client,Server: Client automatically discovers available tools via MCP Schema
    Client->>Server: tools/call: search_docs(query, top_k=4)
    Server->>Embedder: Convert query to high-dimensional vector
    Embedder-->>Server: 3,072-dimension mathematical vector
    Server->>Store: Vector cosine-similarity search
    Store-->>Server: Top relevant documentation chunks + source metadata
    Server-->>Client: Formatted text chunks with file citations & relevance scores
    Client-->>User: Synthesized technical response with verified citations

```

---

## ✨ Key Architectural Innovations

### 1. Multi-Client Portability

* Verified across autonomous multi-step reasoning agents (LangGraph issue triage pipeline).
* Verified across off-the-shelf consumer applications (Anthropic's Claude Desktop).
* **Zero code modifications** needed on the server to switch or add consuming AI clients.

### 2. Client Dependency Elimination

* AI agents no longer carry heavy vector database libraries or embedding dependencies.
* Consuming agent packages remain ultra-lightweight, calling retrieval over standard text pipes.

### 3. Protocol Safety & Intent Contracts

* Incorporates tool execution annotations informing consuming LLMs of operational safety:
* **Read-Only Guarantee:** Guarantees no persistent state modification on execution.
* **Non-Destructive Execution:** Signals safe invocation without side effects.
* **Idempotency:** Guarantees identical parameters yield consistent results.



### 4. Resilient Boundary Defense

* Enforces strict validation parameters to eliminate blank queries and out-of-bounds requests.
* Isolated diagnostic telemetry prevents protocol stream corruption, ensuring seamless tool discovery.

---

## 🧭 Live Client Topology

```mermaid
graph LR
    subgraph Clients ["Verified Consumer Ecosystem"]
        direction TB
        C1["🤖 Autonomous LangGraph Agent\n(GitHub Issue Triage)"]
        C2["💬 Anthropic Claude Desktop\n(Interactive Desktop Assistant)"]
    end

    subgraph Hub ["Universal Interop Layer"]
        Bridge["Model Context Protocol (stdio Bus)"]
    end

    subgraph Engine ["Retrieval Core"]
        direction TB
        Srv["docs-retriever Server"]
        Chroma[("Persistent Vector Collection")]
        Gemini["3,072-Dimensional Embeddings"]
        Srv --- Chroma
        Srv --- Gemini
    end

    C1 ==>|stdio Pipe| Bridge
    C2 ==>|stdio Pipe| Bridge
    Bridge ==> Srv

    classDef clientBox fill:#e6f4ff,stroke:#69b1ff,stroke-width:2px;
    classDef hubBox fill:#f9f0ff,stroke:#d3adf7,stroke-width:2px;
    classDef engineBox fill:#f6ffed,stroke:#95de64,stroke-width:2px;

    class C1,C2 clientBox;
    class Bridge hubBox;
    class Srv,Chroma,Gemini engineBox;

```

---

## 📊 Core Tool Capabilities

| Capability | Specification | Architectural Role |
| --- | --- | --- |
| **Tool Name** | `search_docs` | Primary entry point for natural language document discovery. |
| **Input Constraints** | Bounded queries & parameter thresholds | Prevents malformed database operations before execution. |
| **Metadata Extraction** | Sources, file paths, and relative scores | Enables conversational LLMs to generate accurate technical citations. |
| **Execution Transport** | Standard Input / Output (`stdio`) | Subprocess lifecycle binding without networking overhead. |
| **Protocol Compliance** | MCP v2 Stateless Architecture | Self-describing requests via modern metadata standards. |

---

## 📈 Quality & Reliability Standards

The retrieval engine undergoes automated end-to-end evaluation to guarantee reliability across edge cases and high-concurrency requests:

* **Semantic Precision:** Evaluated against technical topics including authentication scopes, dependency injection, and middleware.
* **Citation Integrity:** Document chunks return exact source file names and relevance scores.
* **Defensive Edge Defense:** Rejects empty queries, whitespace inputs, and invalid limits with non-crashing structured responses.
* **Deterministic Execution:** Sub-second retrieval latency across local vector indices.

---

## 🔍 Verified Proof of Portability

> *"Anthropic's Claude Desktop discovering and executing retrieval against local vector documentation through `docs-retriever-mcp` with zero custom server modifications."*

---

