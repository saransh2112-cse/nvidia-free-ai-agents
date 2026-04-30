# 🕸️ NVIDIA AI Free Agent Blueprints (5 Days, 5 Blueprints)

Welcome to the open-source repository for the **NVIDIA AI Agent Masterclass**. This repository contains 5 high-performance, free-to-run agentic blueprints built using NVIDIA NIMs and Llama 3.1.

## 🚀 The Blueprints

### Day 1: Multi-Agent Debate Arena ⚔️
A multi-agent workflow where two LLMs debate a topic, moderated by a third agent. 
- **Model**: `meta/llama-3.1-8b-instruct`

### Day 2: Enterprise Model Router 🚦
A Streamlit-based evaluator that routes prompts to different NVIDIA-hosted models and compares latency/quality.
- **Models**: Multi-model (Llama, Mistral, Nemotron)

### Day 3: Asynchronous Research Swarm 🕵️‍♂️
A high-speed research swarm that spawns multiple agents in parallel for deep-dive web analysis.
- **Model**: `meta/llama-3.1-8b-instruct`

### Day 4: 3D Knowledge Graph Swarm 🕸️
A swarm of agents that deconstructs a topic and visualizes the "mental model" in a cinematic 3D interactive space.
- **Model**: `meta/llama-3.1-8b-instruct`

### Day 5: Self-Healing Code Auditor 🛡️ (GRAND FINALE)
An autonomous security agent that scans Python code for vulnerabilities and **automatically generates the healed code refactor.**
- **Model**: `meta/llama-3.1-8b-instruct`
- **Tech**: FastAPI + Security HUD UI

---

## 🤝 Join the Community & Contribute
We are building a library of free, high-performance agent blueprints. 

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
4. Run any blueprint: `cd IdeaX && python -m uvicorn app:app`
