# Open Brain

A local, self-hosted AI knowledge base that provides persistent, semantically searchable memory to any AI coding assistant or agent via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

---

## Table of Contents

- [The Problem](#the-problem)
- [What Open Brain Does](#what-open-brain-does)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Available Tools](#available-tools)
- [Use Cases](#use-cases)
- [Setup](#setup)
- [Connecting to AI Tools](#connecting-to-ai-tools)
- [Corporate Deployment Considerations](#corporate-deployment-considerations)
- [Roadmap](#roadmap)

---

## The Problem

Modern AI-assisted development suffers from three compounding issues:

### 1. Amnesia Across Sessions

Every time a developer opens a new AI session — whether in ChatGPT, Claude, Cursor, Copilot, or any other tool — the AI starts from zero. It has no memory of past conversations, decisions, debugging sessions, or project context. Developers are forced to re-explain their architecture, coding standards, business constraints, and past troubleshooting steps repeatedly. This is not a minor inconvenience; it is a measurable productivity drain that scales with team size.

### 2. Siloed Platform Memory

Some AI platforms have introduced "memory" features (ChatGPT memory, Claude Projects, etc.), but these memories are trapped inside their respective platforms. Knowledge saved in ChatGPT is invisible to Claude. Context built in Cursor doesn't transfer to VS Code Copilot. This creates vendor lock-in and fragments institutional knowledge across walled gardens that the developer — and especially the organization — does not own or control.

### 3. Human-Centric Knowledge Tools Don't Serve Agents

Traditional knowledge management tools (Confluence, Notion, SharePoint, Google Docs) are built for human consumption. They organize information visually — folders, pages, rich formatting. AI agents can't efficiently navigate these structures. They need infrastructure built for machine readability: structured data, semantic search via vector embeddings, and programmatic access via standard protocols.

**The net result:** developers and organizations are paying for AI tools that can't learn, can't remember, and can't share context — not because the technology doesn't exist, but because no shared knowledge layer connects them.

---

## What Open Brain Does

Open Brain is a **local MCP server** backed by a **vector database** that acts as a shared, persistent brain for all of your AI tools.

- **Save** decisions, insights, debugging solutions, architectural patterns, coding standards, project context, or anything else worth remembering
- **Search** by meaning, not just keywords — ask "how did we handle authentication?" and find relevant results even if the word "authentication" doesn't appear in the stored text
- **Connect** any MCP-compatible AI tool to the same brain — Claude Code, Cursor, VS Code with Copilot, custom agents, CI/CD pipelines, or internal tooling
- **Own** your data completely — everything runs locally on your machine (or your organization's infrastructure), nothing is sent to any cloud service

The key insight is that **MCP is the "USB-C of AI"** — it is a standardized protocol that any compliant tool can speak. By building the knowledge layer on MCP, Open Brain is tool-agnostic by default. You are not building for Claude or for ChatGPT; you are building a knowledge base that any current or future AI tool can connect to.

---

## How It Works

### Vector Embeddings and Semantic Search

When you save a thought to Open Brain, the text is converted into a **vector embedding** — a high-dimensional numerical representation of the *meaning* of the text. These embeddings are stored in ChromaDB, a purpose-built vector database.

When you search, your query is also converted into a vector, and ChromaDB finds stored thoughts whose vectors are closest in meaning to your query using **cosine similarity**. This means:

- Searching "database performance issues" will find a thought about "slow SQL queries causing timeouts" — even though they share no words in common
- Searching "how we deploy to production" will surface relevant CI/CD decisions, deployment checklists, and infrastructure notes
- The more knowledge you store, the more useful every future search becomes

### The MCP Protocol

The [Model Context Protocol](https://modelcontextprotocol.io/) is an open standard created by Anthropic that defines how AI applications communicate with external tools and data sources. It works like a USB port for AI: any AI tool that supports MCP can connect to any MCP server.

Open Brain exposes its capabilities as **MCP tools** — standardized function definitions that AI assistants can discover, understand, and invoke. When Claude Code (or Cursor, or any other MCP client) connects to Open Brain, it sees the available tools (`save_thought`, `search_brain`, etc.) and can use them naturally as part of its workflow.

### The Compounding Effect

This system creates a **compounding advantage** over time:

1. **Day 1:** You save your first few architectural decisions and coding standards
2. **Week 1:** Your AI assistants already know your project structure, naming conventions, and key constraints
3. **Month 1:** Debugging insights, past incidents, API quirks, and team decisions are all searchable
4. **Month 6:** You have a comprehensive institutional knowledge base that makes every AI interaction dramatically more productive
5. **Year 1:** New team members' AI tools can immediately access the full history of decisions, patterns, and lessons learned

Every thought you save makes every future AI interaction more informed. The brain never forgets, never loses context, and is always available to every tool you use.

---

## Architecture

```
+------------------+     +------------------+     +------------------+
|   Claude Code    |     |     Cursor       |     |   Custom Agent   |
|   (MCP Client)   |     |   (MCP Client)   |     |   (MCP Client)   |
+--------+---------+     +--------+---------+     +--------+---------+
         |                         |                         |
         |        MCP Protocol (stdio / HTTP)                |
         |                         |                         |
         +------------+------------+-------------------------+
                      |
              +-------+--------+
              |  Open Brain    |
              |  MCP Server    |
              |  (Python)      |
              +-------+--------+
                      |
              +-------+--------+
              | ChromaDB       |
              | (Vector DB)    |
              | Local on disk  |
              +----------------+
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| MCP Server | Python + FastMCP (`mcp` SDK) | Exposes brain operations as MCP tools |
| Vector Database | ChromaDB (persistent mode) | Stores thoughts with vector embeddings, handles semantic search |
| Embedding Model | ChromaDB default (all-MiniLM-L6-v2 via ONNX Runtime) | Converts text to vector embeddings locally — no API calls |
| Transport | stdio (local) or HTTP (network) | Communication between AI tools and the brain |

### Data Flow

1. **Save:** AI tool calls `save_thought` -> MCP server receives the text -> ChromaDB generates a vector embedding locally -> text + embedding + metadata are stored to disk
2. **Search:** AI tool calls `search_brain` with a natural language query -> MCP server passes query to ChromaDB -> ChromaDB embeds the query and finds nearest neighbors by cosine similarity -> ranked results returned to AI tool
3. **Persistence:** ChromaDB stores all data in the local `data/` directory as files. No external database process is required. Data survives restarts, updates, and tool changes.

---

## Available Tools

Open Brain exposes six MCP tools that any connected AI assistant can invoke:

### `save_thought`
Save a thought, note, decision, or piece of knowledge to the brain.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | The thought or knowledge to save |
| `tags` | string | No | Comma-separated tags (e.g. `"python,debugging,tip"`) |
| `category` | string | No | One of: `general`, `decision`, `insight`, `reference`, `project`, `preference` |

### `search_brain`
Semantically search the brain for relevant thoughts. Returns results ranked by similarity.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `n_results` | int | No | Number of results to return (default: 5) |
| `category` | string | No | Filter results by category |

### `list_recent`
List the most recent thoughts in the brain, optionally filtered by category.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `n` | int | No | Number of recent thoughts to return (default: 10) |
| `category` | string | No | Filter by category |

### `delete_thought`
Delete a thought from the brain by its UUID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thought_id` | string | Yes | The UUID of the thought to delete |

### `update_thought`
Update the content, tags, or category of an existing thought.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thought_id` | string | Yes | The UUID of the thought to update |
| `content` | string | No | New content |
| `tags` | string | No | New comma-separated tags |
| `category` | string | No | New category |

### `brain_stats`
Get statistics about the brain — total thought count, category breakdown, and top tags. Takes no parameters.

---

## Use Cases

### Individual Developer Productivity

- **Persistent project context:** Save your project's architecture, tech stack, key constraints, and coding standards. Every AI session starts with full context instead of from zero.
- **Debugging knowledge base:** When you solve a tricky bug, save the root cause and fix. Next time you (or your AI) encounter something similar, semantic search surfaces the solution.
- **Decision log:** Record why you chose React over Vue, PostgreSQL over MongoDB, microservices over monolith. When the question comes up again in 6 months, the reasoning is instantly retrievable.
- **Code pattern library:** Save patterns, idioms, and templates specific to your codebase that AI tools should follow when generating code.

### Team Knowledge Sharing

- **Onboarding acceleration:** New developers' AI tools immediately have access to the team's accumulated decisions, patterns, and institutional knowledge. Instead of asking "how does our auth work?" to a senior dev, they ask their AI — which searches the shared brain.
- **Cross-tool consistency:** Whether a team member uses Claude, Cursor, Copilot, or a custom internal tool, they all access the same knowledge base. No more "I had this in my ChatGPT history somewhere."
- **Incident response memory:** Post-incident reviews, root causes, and fixes are saved and semantically searchable. When similar symptoms appear, any AI tool can find past incidents.

### Corporate / Enterprise Applications

- **Institutional knowledge preservation:** When senior engineers leave, their knowledge doesn't walk out the door. Decisions, context, and expertise persist in the brain.
- **Compliance and audit trail:** Every decision and its rationale is stored with timestamps. Useful for regulated industries where you need to demonstrate why specific technical choices were made.
- **AI tool evaluation:** Since Open Brain is tool-agnostic via MCP, organizations can evaluate and switch between AI tools without losing their accumulated knowledge base. No vendor lock-in.
- **Internal documentation that AI can actually use:** Instead of (or in addition to) maintaining Confluence pages that AI tools can't efficiently parse, save structured knowledge to the brain where it's immediately machine-readable and semantically searchable.
- **Multi-agent orchestration:** In advanced setups, multiple AI agents working on different parts of a project can share a single brain. Agent A's architectural decisions are immediately visible to Agent B's implementation work.

### CI/CD and Automation Integration

- **Build failure knowledge:** CI pipelines can write failure patterns and solutions to the brain. When a developer encounters a similar failure, their AI already knows the fix.
- **Deployment checklists:** Save deployment procedures, environment-specific quirks, and rollback steps. AI assistants can retrieve them at the relevant moment.
- **API changelog memory:** When external APIs change behavior, save the observation. Future AI sessions that interact with those APIs start informed.

---

## Setup

### Prerequisites

- **Python 3.10+**
- **uv** (recommended) or pip for dependency management

### Installation

```bash
# Clone the repository
git clone https://github.com/WintersRain/open-brain.git
cd open-brain

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Running the Server

The server is designed to be launched automatically by MCP clients (like Claude Code), not run manually. However, you can test it:

```bash
# Via uv
uv run python src/server.py

# The server communicates over stdio — it will appear to hang
# because it's waiting for MCP protocol messages on stdin.
# This is expected. Press Ctrl+C to exit.
```

---

## Connecting to AI Tools

### Claude Code

```bash
claude mcp add --transport stdio open-brain -- \
  python -m uv run --directory /path/to/open-brain python src/server.py
```

Once added, Claude Code will automatically start the server when needed. You can verify with:

```bash
claude mcp list
```

You should see `open-brain` with status `Connected`.

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json` or global settings):

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/open-brain", "python", "src/server.py"]
    }
  }
}
```

### VS Code (with MCP-compatible extension)

Add to your VS Code MCP configuration (location varies by extension):

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/open-brain", "python", "src/server.py"]
    }
  }
}
```

### Any MCP Client

The server uses **stdio transport** by default. Point any MCP client at:

```
command: uv run --directory /path/to/open-brain python src/server.py
transport: stdio
```

---

## Corporate Deployment Considerations

This prototype is a single-user, local-only implementation. Scaling it for corporate use involves several architectural decisions:

### Database Backend

The current implementation uses **ChromaDB in embedded/local mode**, which stores data as files on disk. For corporate deployment, consider:

- **ChromaDB server mode:** ChromaDB can run as a standalone server, allowing multiple clients to connect to a shared instance over HTTP
- **PostgreSQL + pgvector:** For organizations already running PostgreSQL, the pgvector extension provides vector search capabilities within an existing, battle-tested database. This is the most operationally familiar option for most engineering teams.
- **Dedicated vector databases:** Pinecone, Weaviate, Milvus, or Qdrant for large-scale deployments with millions of entries

### Embedding Model

The current implementation uses ChromaDB's default embedding model (`all-MiniLM-L6-v2` via ONNX Runtime), which runs locally with zero API calls. For corporate deployment:

- **Local models via Ollama:** Models like `nomic-embed-text` or `mxbai-embed-large` provide higher quality embeddings while still running on-premises
- **OpenAI / Anthropic / Cohere embedding APIs:** Higher quality embeddings at the cost of per-request API fees and data leaving the network
- **Self-hosted models:** Deploy embedding models on internal GPU infrastructure for maximum quality without data leaving the organization

### Authentication and Authorization

The current implementation has no authentication — anyone who can reach the server can read and write. For corporate deployment:

- **Per-user brains:** Each developer gets their own isolated brain, or a shared team brain with personal overlays
- **Role-based access control:** Read-only access for junior devs, write access for seniors, admin access for leads
- **API key / OAuth integration:** Tie into existing corporate identity providers (Okta, Azure AD, etc.)
- **Audit logging:** Log all reads and writes for compliance

### Transport

The current implementation uses **stdio** (standard input/output), which only works for local, same-machine connections. For network deployment:

- **HTTP transport:** The MCP SDK supports HTTP transport out of the box. Switch from `mcp.run()` to `mcp.run(transport="http")` to enable network access.
- **TLS/HTTPS:** Required for any non-local deployment
- **Load balancing:** Standard HTTP load balancers work for horizontal scaling

### Data Management

- **Backup and restore:** ChromaDB's data directory can be backed up with standard file-level tools. PostgreSQL-based deployments use standard pg_dump.
- **Data retention policies:** Implement automatic expiration of old thoughts, or archive-and-purge cycles
- **Data classification:** Tag thoughts with sensitivity levels to control what gets shared vs. kept private
- **Export/import:** Build tooling to migrate between backends or export for compliance requests

### Multi-Tenancy

- **Team-scoped brains:** Separate ChromaDB collections per team, project, or department
- **Cross-team search:** Federated search across multiple brains with appropriate access controls
- **Shared organizational brain:** A read-only brain containing company-wide standards, patterns, and decisions that every developer's AI tools can access

---

## Roadmap

Potential enhancements for future development:

- [ ] **HTTP transport mode** — enable network access for shared/team deployments
- [ ] **Ollama embedding integration** — swap to higher-quality local embeddings
- [ ] **Import/export** — bulk load from Markdown files, Notion exports, Confluence dumps
- [ ] **Thought linking** — connect related thoughts into knowledge graphs
- [ ] **Auto-capture hooks** — automatically save decisions from git commit messages, PR descriptions, or Slack threads
- [ ] **Web UI** — browser-based interface for browsing and managing the brain without an AI tool
- [ ] **Multi-collection support** — separate brains per project or team within a single server
- [ ] **PostgreSQL + pgvector backend** — drop-in replacement for ChromaDB for enterprise deployments

---

## Tech Stack

| Component | Version | License |
|-----------|---------|---------|
| Python | 3.10+ | PSF |
| MCP SDK (`mcp`) | 1.0+ | MIT |
| ChromaDB | 0.6+ | Apache 2.0 |
| ONNX Runtime | (bundled with ChromaDB) | MIT |
| all-MiniLM-L6-v2 | (bundled with ChromaDB) | Apache 2.0 |

Total dependencies: ~90 Python packages (most are transitive from ChromaDB). No JavaScript, no Docker, no external services.

---

## Cost

**$0.** Everything runs locally. No cloud services, no API keys, no subscriptions, no per-request fees. The embedding model runs on CPU via ONNX Runtime — no GPU required.

---

## License

MIT
