# 🧠 NVIDIA Free Enterprise AI Agents
### *Building AI agents that solve 7-figure business problems. Free & Open Source.*

[![NVIDIA NIM](https://img.shields.io/badge/Powered%20by-NVIDIA%20NIM-76b900?style=flat-square&logo=nvidia)](https://build.nvidia.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

Welcome to the open-source repository for the **30-Day Enterprise Agent Challenge** — a series of production-grade AI agents built using NVIDIA NIMs and Llama 3.1. No paid APIs. No SaaS subscriptions. Just powerful agentic AI, free forever.

---

## 📦 Phase 1 — AI Blueprints (Days 1–5)
> *Foundation agentic patterns using NVIDIA's hosted models.*

| Day | Agent | Description | Port |
|-----|-------|-------------|------|
| 1 | ⚔️ **Multi-Agent Debate Arena** | Two LLMs debate a topic, moderated by a third agent | 8001 |
| 2 | 🚦 **Enterprise Model Router** | Routes prompts to NVIDIA-hosted models, benchmarks latency & quality | 8002 |
| 3 | 🕵️ **Async Research Swarm** | Parallel agents for high-speed deep-dive web research | 8003 |
| 4 | 🕸️ **3D Knowledge Graph Swarm** | Deconstructs a topic into a cinematic 3D interactive knowledge graph | 8004 |
| 5 | 🛡️ **Self-Healing Code Auditor** | Scans Python code for vulnerabilities and auto-generates secure refactors | 8005 |

---

## 🏛️ Phase 2 — Enterprise Agent Series (Days 6–15)
> *AI agents solving real 7-figure business problems. Free.*

| Day | Agent | Business Problem Solved | Port |
|-----|-------|------------------------|------|
| 6  | 🏛️ **Oracle Boardroom** | Replaces $50K strategy consultants — 5 C-suite AI executives debate decisions with LIVE market data | 8006 |
| 7  | 📊 **Sales Nexus** | AI-powered sales intelligence and lead conversion engine | 8007 |
| 8  | 💰 **M&A Intelligence** | Autonomous due diligence swarm for mergers & acquisitions | 8008 |
| 9  | 🚨 **PR Crisis Sentinel** | Real-time brand crisis detection and autonomous response drafting | 8009 |
| 10 | 💓 **BrandPulse Swarm** | Real-time brand sentiment and risk analysis swarm for enterprise reputation management | 8010 |
| 11 | ⚖️ **Contract Negotiator** | Legal swarm that audits contracts and drafts counter-offers | 8011 |
| 12 | 🚢 **Atlas Logistics** | Live global supply chain disruption detection and autonomous re-routing | 8012 |
| 13 | 🧪 **Vinci R&D** | Patent intelligence, market gap analysis, and autonomous product design | 8013 |
| 14 | 📉 **Echo — Churn Engine** | Predicts customer churn risk and auto-generates personalized retention offers | 8014 |
| 15 | 🧲 **Vertex — Talent Engine** | Detects employee flight risk and builds personalized retention packages | 8015 |

---

## 🏔️ Phase 3 — The Apex Industry Series (Days 16–30)
> *"Building the Apex of Industry Intelligence. 15 industries. 15 swarms."*

| Day | Agent Name | Industry | Mission |
|:---:|---|---|---|
| 16 | 🏥 **Bio-Scribe** | Healthcare | Autonomous patient triage & clinical trial matching swarm. |
| 17 | ⚖️ **Lex-Titan** | Legal Tech | High-speed case law researcher & automated litigation drafter. |
| 18 | 🏨 **Nomad-OS** | Travel/HRS | Multi-agent hotel procurement & negotiation swarm. |
| 19 | 🏗️ **Skyline-AI** | Real Estate | Autonomous property valuation & urban zoning compliance auditor. |
| 20 | ⚡ **Volt-Grid** | Energy/Utility | Live energy market arbitrage & grid disruption prediction agent. |
| 21 | 🎬 **Studio-Flow** | Media/Ent | Script breakdown, autonomous casting, and production budgeting swarm. |
| 22 | 📦 **Supply-Sync** | E-commerce | Multi-vendor inventory negotiation & automated stock-out prevention. |
| 23 | 🌾 **Agri-Brain** | Agriculture | Satellite-data-driven crop yield predictor & commodity pricing scout. |
| 24 | 🛡️ **Cyber-Wall** | Cybersecurity | Autonomous red-team penetration testing & zero-day patch drafter. |
| 25 | 🎓 **Edu-Forge** | EdTech | Personalized curriculum architect & autonomous student mentor swarm. |
| 26 | 🏦 **DeFi-Sentry** | Finance/Crypto | Multi-chain fraud detection & autonomous yield optimization strategist. |
| 27 | 🚚 **Fleet-Commander**| Logistics | Real-time trucking route optimizer & fuel cost minimization engine. |
| 28 | 🧪 **Molecule-X** | Pharma/R&D | AI-driven drug discovery swarm & chemical property predictor. |
| 29 | 🗳️ **Civic-Core** | GovTech | Public policy impact analyzer & automated citizen request handler. |
| 30 | 🛸 **Quantum-Nexus**| Future-Tech | **The Grand Finale**: A "Super-Agent" that orchestrates all previous 29 agents. |

---

## 🛠️ Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/umang-algo/nvidia-free-ai-agents.git
cd nvidia-free-ai-agents

# 2. Get your FREE NVIDIA API Key at https://build.nvidia.com/
# 3. Create a .env file
echo "NVIDIA_API_KEY=your_key_here" > .env

# 4. Run any agent (replace X with the idea number)
cd IdeaX_AgentName && python3 -m uvicorn app:app --port 80XX --reload
```

### Requirements
```bash
pip install fastapi uvicorn openai httpx python-dotenv pydantic
```

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM Inference** | NVIDIA NIM (Llama 3.1 8B Instruct) — Free tier |
| **Backend** | FastAPI + asyncio (parallel agent execution) |
| **Live Data** | Yahoo Finance API + Reuters RSS feeds |
| **Frontend** | Vanilla HTML/CSS/JS (no frameworks) |
| **Concurrency** | `asyncio.gather()` — all agents run in parallel |

---

## 🤝 Contribute & Join the Mission

We're building the world's largest library of **free enterprise AI agents**.

**Have an idea for a new enterprise agent?**
1. **Fork** this repository
2. **Build** your agent in a new `IdeaXX_AgentName/` folder
3. **Submit a Pull Request**
4. Get added as an **Official Open Source Contributor** 🏆

> 💬 Drop your agent idea in the Issues tab — the community votes on what gets built next.

---

## ⭐ Star History
If this helped you, give it a star. It helps more builders find these free tools.

*Built with ❤️ using [NVIDIA NIM](https://build.nvidia.com/) — free, fast, powerful.*
