# Running the Tennis Scheduler AI Agent Locally

This document explains how to run the Tennis Scheduler AI Agent locally using
**Streamlit** for the UI and **Ollama** for LLM inference and embeddings.

---

## Prerequisites

Make sure you have the following installed:

- Python 3.11 or higher
- Git
- Ollama: https://ollama.ai

* If you would like to enable agentic response tracing and evaluation on LangSmith, add following this in the .env file

    - LANGCHAIN_TRACING_V2=true
    - LANGCHAIN_PROJECT=<PROJECT_NAME>
    - LANGCHAIN_API_KEY=<LANGSMITH_API_KEY>

---

## 1. Clone the Repository

```bash
git clone https://github.com/RutanshuDesai/agentic_tennis_app.git
cd agentic_tennis_app

python3.11 -m venv .venv
source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt

ollama pull nomic-embed-text
ollama pull gpt-oss

streamlit run tennis_agent_app/app.py
```

Application available at: http://localhost:8501


## 2. Creating your own document vector index

```bash
Edit parameters and run "sample_build_index.py" to create your own index and use the vector index for the agent.
```




Ask sample questions like - 
- What model are you running?
- What can you help me with?
- what is the weather in fuquay at 2pm
- how is the weather in fuquay at 8am on jan 1 2026
- how is the weather in hollyspring on sunday jan 4th at 10am? also can you tell me the weather starting saturday 7pm to sunday 12pm in a table format? make sure the table has the correct dates and data.
- schedule a tennis match at 10am on Jan 5th 2026 at cary
