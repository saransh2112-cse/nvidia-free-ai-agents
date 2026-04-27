# 🚀 NVIDIA AI Agent Blueprints

This repository contains 5 high-value, open-source AI agent applications. **The best part? It's TOTALLY FREE.** 

We are leveraging NVIDIA's free API endpoints (`integrate.api.nvidia.com/v1`) using OpenAI-compatible SDKs. You don't need to pay for ChatGPT or Anthropic to experiment with powerful agentic workflows, multi-model communication, asynchronous streaming, and structured data extraction. Build advanced AI tools at zero cost!

## Setup Instructions

1. Get your free NVIDIA API Key from [build.nvidia.com/models](https://build.nvidia.com/models)
2. Rename `.env.template` to `.env` and paste your key:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` to contain: `NVIDIA_API_KEY=nvapi-...`
3. Install the dependencies:
   ```bash
   pip install pyautogen streamlit openai python-dotenv fastapi uvicorn pydantic rich
   ```

## Projects Included

### 1. Multi-Model Agent Debate (`Idea1_Debate_App/`)
A beautiful FastAPI web app that streams an autonomous debate between two models: Llama 3.1 70B and Mixtral 8x22B.
- **To run web app:** `cd Idea1_Debate_App && python3 -m uvicorn app:app --port 8050`
- **To run AutoGen version:** `python Idea1_Debate_App/autogen_version.py`

### 2. Enterprise Model Routing Intelligence (`Idea2_Enterprise_Model_Router/`)
A Streamlit dashboard that dynamically benchmarks Latency, Throughput (Tokens/sec), and ROI across multiple NVIDIA endpoints to help you choose the best model for specific business tasks.
- **To run:** `cd Idea2_Enterprise_Model_Router && streamlit run app.py`

### 3-5. Coming Soon! 🚀
Over the next few days, I will be pushing 3 more fully-functional, free AI Agent blueprints to this repository, including:
- 🐝 An Asynchronous Research Swarm
- 🔄 A Viral Content Repurposer
- 📊 A Structured Data Extractor

Watch this space!

## Contributing
Feel free to open issues or PRs if you want to add more ideas!
