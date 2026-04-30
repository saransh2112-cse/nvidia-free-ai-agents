# 🕸️ NVIDIA AI Free Agent Blueprints (5 Days, 5 Blueprints)

Welcome to the open-source repository for the **NVIDIA AI Agent Masterclass**. This repository contains high-performance, free-to-run agentic blueprints built using NVIDIA NIMs and Llama 3.1.

## 🚀 The Blueprints

### Day 1: Multi-Agent Debate Arena ⚔️
A multi-agent workflow where two LLMs debate a topic, moderated by a third agent. Shows how to handle agent-to-agent communication.
- **Model**: `meta/llama-3.1-8b-instruct`
- **Tech**: FastAPI + HTML/JS

### Day 2: Enterprise Model Router 🚦
A Streamlit-based evaluator that routes prompts to different NVIDIA-hosted models and compares latency and response quality.
- **Model**: Multi-model (Llama, Mistral, Nemotron)
- **Tech**: Streamlit

### Day 3: Asynchronous Research Swarm 🕵️‍♂️
A high-speed research swarm that spawns multiple agents in parallel to perform deep-dive web analysis on any topic.
- **Model**: `meta/llama-3.1-8b-instruct`
- **Tech**: Asynchronous Python + Streamlit

### Day 4: 3D Knowledge Graph Swarm 🕸️ (LATEST)
Our most advanced blueprint yet. A swarm of agents that deconstructs a topic and visualizes the "mental model" in a cinematic 3D interactive space.
- **Key Feature**: Click nodes to "fly into" the research insights.
- **Model**: `meta/llama-3.1-8b-instruct`
- **Tech**: FastAPI + 3D-Force-Graph (WebGL)

---

## 🤝 Join the Community & Contribute
This is an open-source project aimed at making agentic AI accessible to everyone. We want YOU to help us build the future of agents.

**How to contribute:**
1.  **Fork** the repository.
2.  **Add** a new agent blueprint or improve an existing one.
3.  **Submit a Pull Request**.
4.  Get added to our **Open Source Contributor** list!

---

## 🛠️ Getting Started
1. Clone the repo: `git clone https://github.com/umang-algo/nvidia-free-ai-agents.git`
2. Get your free NVIDIA API Key at [NVIDIA NIM](https://build.nvidia.com/).
3. Add your key to a `.env` file: `NVIDIA_API_KEY=your_key_here`
4. Run any idea: `cd IdeaX && python -m uvicorn app:app` or `streamlit run app.py`
