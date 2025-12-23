# 🎾 Tennis Scheduler — Agentic AI Personal Assistant

An **agentic AI scheduling assistant** that helps coordinate tennis matches and fitness activities by reasoning over availability, weather, and recovery constraints.

This project focuses on **agent orchestration, tool design, and observability**, rather than novel ML algorithms.

---

## Project Status

This project is intentionally in an **early, iterative stage**.

Its primary goal is to explore **agent design patterns, constraint-based reasoning, and tool orchestration** using LangChain, rather than deliver a fully polished consumer application.

Several production-grade agentic systems I’ve built professionally cannot be open-sourced, so this repository serves as a **public, self-directed exploration** of agentic workflows and architectural trade-offs.

---

## Problem

Scheduling tennis matches—especially in ladder-style tournaments—is deceptively complex.

To accept or propose a match, I need to:
- Check calendar availability
- Verify playable weather conditions
- Respect recovery constraints (e.g., no tennis after heavy workout days)
- Propose multiple candidate time slots when needed

As constraints increase, manual scheduling becomes inefficient and error-prone.

---

## Solution: An Agentic Scheduling System

This project implements an **agent-based system** that decomposes scheduling into structured reasoning steps and tool calls.

The agent understands natural language prompts such as:

> *“Can I play tennis tomorrow at 5 PM at Cary Tennis Park?”*

And autonomously:
- Evaluates feasibility
- Explains decisions
- Suggests alternatives when constraints fail

---

## Agent Design

The system is built using **LangChain v1**, with a deliberate focus on **clarity, extensibility, and observability**.

### High-level reasoning flow
1. Intent parsing
2. Constraint evaluation:
   - Calendar availability
   - Weather conditions
   - Workout and recovery rules
3. Decision:
   - Accept proposed time  
   - OR suggest alternative slots
4. Human-in-the-loop confirmation
5. Action execution (calendar event creation)

Each step is explicit, inspectable, and debuggable.

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

- 📅 **Google Calendar Tool**  
  Checks conflicts, availability, and scheduling constraints

- 🌦 **Weather Tool**  
  Enforces minimum playable conditions:
  - Temperature: 35°F – 85°F  
  - Wind: < 10 mph  
  - No rain or storms

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

All agent reasoning, prompts, and tool executions are tracked using **LangSmith**.

This enables:
- Full trace inspection
- Debugging incorrect decisions
- Understanding why alternatives were suggested

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

- **LangChain v1** — agent framework
- **LangGraph** — planned for explicit state management
- **ChromaDB** — local vector store for RAG
- **Unstructured** — document ingestion
- **LLMs** — OpenAI / DBRX (configurable)
- **Streamlit** — lightweight UI
- **Docker** — portable deployment
- **FastMCP** — standardized tool interfaces

---

## Notes

This project emphasizes:
- Agent design trade-offs
- Tool orchestration
- Observability
- Production-minded decision making

It is intentionally scoped as a **personal system** to experiment with agentic patterns applicable to larger, real-world applications.


