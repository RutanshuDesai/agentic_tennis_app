# Running the Tennis Scheduler AI Agent Locally

This document explains how to run the Tennis Scheduler AI Agent locally using
**Streamlit** for the UI and **Ollama** for LLM inference and embeddings.

---

## Prerequisites

Make sure you have the following installed:

- Python 3.11 or higher
- Git
- Ollama: https://ollama.ai

---

## 1. Clone the Repository

```bash
git clone https://github.com/RutanshuDesai/agentic_tennis_app.git
cd <repo-name>

python3.11 -m venv .venv
source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt

ollama pull nomic-embed-text
ollama pull gpt-oss

streamlit run app.py
```

Application available at: http://localhost:8501

Ask sample questions like - 
- What model are you running?
- What can you help me with?
