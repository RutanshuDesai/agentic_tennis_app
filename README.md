# 🎾 Tennis Scheduler — Agentic AI Personal Assistant

An **agentic AI scheduling assistant** that helps coordinate tennis matches and fitness activities by reasoning over availability, weather, and recovery constraints.

This project focuses on **agent orchestration, tool design, and observability**.

---

## Project Status

This project is intentionally in an **early, iterative stage**.

Its primary goal is to explore **agent design patterns, constraint-based reasoning, and tool orchestration** using LangChain, rather than deliver a fully polished consumer application.

Several production-grade agentic systems I’ve built professionally cannot be open-sourced, so this repository serves as a **public, self-directed exploration** of agentic workflows and architectural trade-offs.

---

## Embeddings & LLM Setup

This project supports three LLM backends, giving you the flexibility to run locally or in the cloud:

- **Ollama** — Run fully local with no paid APIs (default).
- **GCP Vertex AI** — Use Google's hosted Gemini models via a Vertex API key.
- **Databricks** — Use a Databricks-hosted model if you have access to a Databricks workspace.

Select the backend by setting the `MODEL` option when launching the app. Hosted backends can help lower local compute requirements.

---

## Problem

Scheduling tennis matches—especially in ladder-style tournaments—is deceptively complex.

The requirement of the Tennis ladder tournament is that you need to propose matches to players that they can accept, as well as you have the ability to accept the matches proposed by other players. Players with the most points at the end of the tournament qualify for knockout rounds. 

To accept or propose a match, I need to:
- Check my calendar availability
- Verify playable weather conditions
- Respect recovery constraints (e.g., no tennis after heavy workout days)
- Propose multiple candidate time slots when needed

As constraints increase, manual scheduling becomes inefficient and error-prone.

More details on the problem statement available in the file - [problem_statement.md](./problem_statement.md)

---

## Solution: An Agentic Scheduling System

This project implements an **agent-based system** that decomposes scheduling into structured reasoning steps and tool calls.

The agent understands natural language prompts such as:

> *“Can I play tennis tomorrow at 5 PM at Cary Tennis Park?”*

And autonomously:
- Evaluates feasibility
- Explains decisions
- Suggests alternatives when constraints fail
- Creates events on my calendar after human in the loop confirmation

---

## Agent Design

The system is built using **LangChain v1**, with a deliberate focus on **clarity, extensibility, and observability**.

### Operational Workflow
When asked "Can I play tennis on [Date] at [Time] in [Location]?":

1. **Phase 0 — Calendar & History Check**
   - List all calendar events for the requested date and check for conflicts (including a 4-hour post-match buffer).
   - Check the previous day's events — if any contain "workout", "gym", "tennis", or "exercise", the user is too fatigued to play.
2. **Phase 1 — Weather Validation**
   - Fetch hourly forecasts for the requested time and the surrounding buffer window (6 hours before, 4 hours after).
3. **Phase 2 — Reasoning**
   - Compare weather data against playability constraints.
4. **Phase 3 — Verdict**
   - Provide a clear "Playable" or "Not Playable" decision with supporting data.
5. **Phase 4 — Alternative Scan**
   - Offer to scan the rest of the day or weekend for a better window if the requested slot fails.

Each phase is explicit, inspectable, and debuggable.

---

## Agent Abstraction Choice

The current implementation uses LangChain’s `create_agent` abstraction.

At this stage, the workflow is primarily **linear**, with a limited number of tools and well-defined reasoning steps. Introducing a full state graph at this point would be unnecessary complexity.

### Planned evolution
As the system expands to include:
- Branching logic
- Multiple alternative proposals
- Multi-agent coordination
- Retries and recovery paths

The agent will transition to a **LangGraph-based architecture** to enable explicit state management and more complex orchestration.

This progression reflects an intentional, stage-appropriate design choice.

---

## Tools Used by the Agent

- 📅 **Google Calendar Tools**  
  - *List Events* — fetches events for a date range to check conflicts, availability, and prior-day workout history  
  - *Create Event* — books a calendar event after human-in-the-loop confirmation

- 🌦 **Weather Tool**  
  Enforces minimum playable conditions:
  - Temperature: > 40°F and < 90°F  
  - Wind: < 10 mph  
  - Precipitation: 0% rain during the match, 6 hours before, and 4 hours after

- 📄 **Document Retrieval (RAG)**  
  Used for personal scheduling rules and reference documents

---

## Why Agentic (vs Simple LLM Calls)

This problem benefits from an agentic approach because:
- Constraints compound combinatorially
- Reasoning must be stepwise and explainable
- Failures should degrade gracefully
- Alternatives must be generated systematically

Agent-based orchestration enables:
- Deterministic execution paths
- Tool-level transparency
- Easier debugging and iteration

---

## Observability

All agent reasoning, prompts, and tool executions are tracked using **Langfuse** (open-source, self-hostable), with **LangSmith** available as a backup.

This enables:
- Full trace inspection
- Debugging incorrect decisions
- Understanding why alternatives were suggested
- Self-hosted observability with no vendor lock-in

Observability is treated as a **first-class concern**, not an afterthought.

---

## Deployment & Architecture

- Containerized for portability
- Initial deployment via **GCP Cloud Run**
- LLM inference served externally for cost and latency efficiency
- Planned self-hosted deployment on a local server (e.g., Raspberry Pi)

The architecture is cloud-agnostic and designed to evolve with usage.

---

## Upcoming Enhancements

- Suggests multiple feasible time windows when conflicts occur
- Tracks additional fitness activities:
  - Strength training
  - Stability work
  - Endurance sessions
- Balances weekly training load across activities
- Potential integration with ladder tournament platforms

---

## Tech Stack

- **LangChain v1** — quick open source agentic framework
- **LangGraph** — planned for explicit state management
- **Langfuse** — primary observability and response tracing (open-source, self-hostable)
- **LangSmith** — backup observability option (set `LANGCHAIN_TRACING_V2=true` to enable)
- **ChromaDB** — local vector store for RAG. option to scale it if needed. 
- **Unstructured** — document ingestion
- **LLMs** — Three backend options: Ollama (local), GCP Vertex AI, or Databricks
  - Embeddings via Ollama (`nomic-embed-text`)
- **Streamlit** — lightweight UI
- **Docker** — portable deployment, cloud agnostic, local deployment option
- **FastMCP** — standardized tool interfaces (planned)

---

## Notes

This project emphasizes:
- Agent design trade-offs
- Tool orchestration
- Observability
- Production-minded decision making

It is intentionally scoped as a **personal system** to experiment with agentic patterns applicable to larger, real-world applications.

## Running the App

The app runs locally using Streamlit. The LLM backend is configurable — set it to `ollama`, `vertex`, or `databricks` in `app.py`.

See [RUN_LOCAL.md](./RUN_LOCAL.md) for detailed setup and execution steps.

