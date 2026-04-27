import streamlit as st
from openai import AsyncOpenAI
import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Enterprise AI Router", 
    layout="wide", 
    page_icon="🧭",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #10b981;
    }
    
    .winner-card {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 5px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    .response-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        height: 400px;
        overflow-y: auto;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        color: #e2e8f0;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.5);
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Enterprise Model Routing Intelligence")
st.markdown("*Dynamically benchmark Latency, Throughput, and ROI across NVIDIA's free API endpoints to optimize your Agentic Workflows.*")

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key or api_key == "your_api_key_here":
    st.error("⚠️ Please set your NVIDIA_API_KEY in the .env file located in this directory.")
    st.stop()

client = AsyncOpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=api_key
)

models = {
    "Nemotron Mini 4B (Lightning)": "nvidia/nemotron-mini-4b-instruct",
    "Mixtral 8x22B (Balanced)": "mistralai/mixtral-8x22b-instruct-v0.1",
    "Llama 3.1 8B (Fast)": "meta/llama-3.1-8b-instruct"
}

use_cases = {
    "📝 Custom Prompt": "",
    "📄 Data Extraction (Invoice)": """Extract the following fields from this invoice text into valid JSON format only: 
{ "vendor_name": "", "total_amount": "", "invoice_date": "", "line_items": [] }

Text: 'INV-44912 - Acme Corp. Date: Oct 12, 2026. Services rendered: Web Design ($4500), Server Hosting ($200). Total Due: $4700. Please pay within 30 days.'""",
    "😡 Customer Support Routing": """Analyze this customer email and determine: 1. Sentiment (Positive/Neutral/Negative) 2. Urgency (High/Medium/Low) 3. Recommended Department (Billing/Tech/Sales)

Email: 'I have been trying to access my dashboard for 3 days and I keep getting a 500 error! If this isn't fixed today I am cancelling my enterprise subscription immediately.'""",
    "⚖️ Legal Clause Summary": """Summarize the liabilities and obligations for the 'Receiving Party' in simple English.

Clause: 'The Receiving Party shall hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the Disclosing Party. The Receiving Party shall carefully restrict access to Confidential Information to employees, contractors and third parties as is reasonably required...'"""
}

with st.sidebar:
    st.header("🛠️ Configuration")
    selected_use_case = st.selectbox("Select Enterprise Use Case", list(use_cases.keys()))
    
    st.markdown("---")
    st.markdown("### 💰 ROI Calculator")
    st.info("""
    **Cost of running this via paid APIs:**
    - ~ $0.02 / run
    
    **Cost via NVIDIA Free API:**
    - **$0.00**
    """)
    st.markdown("---")
    st.markdown("Built with ❤️ using the [NVIDIA API](https://build.nvidia.com)")

if selected_use_case == "📝 Custom Prompt":
    prompt = st.text_area("Enter your custom prompt:", height=150)
else:
    prompt = st.text_area("Use Case Prompt (Edit if needed):", use_cases[selected_use_case], height=150)

async def fetch_response_stream(model_name, model_id, prompt, placeholder, metrics_placeholder):
    start_time = time.time()
    content = ""
    token_estimate = 0
    try:
        # Update UI to show starting
        placeholder.markdown(f"<div class='response-box'><i>Connecting to {model_name}...</i></div>", unsafe_allow_html=True)
        
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
                # Live UI update
                placeholder.markdown(f"<div class='response-box'>{content}▌</div>", unsafe_allow_html=True)
                
        # Final update to remove cursor
        placeholder.markdown(f"<div class='response-box'>{content}</div>", unsafe_allow_html=True)
        
        word_count = len(content.split())
        token_estimate = int(word_count * 1.3)
    except Exception as e:
        content = f"Error: {e}"
        placeholder.markdown(f"<div class='response-box' style='color: #ef4444;'>{content}</div>", unsafe_allow_html=True)
        token_estimate = 0
        
    end_time = time.time()
    latency = end_time - start_time
    tps = token_estimate / latency if latency > 0 else 0
    
    # Update metrics when done
    with metrics_placeholder.container():
        m1, m2 = st.columns(2)
        m1.metric("Latency", f"{latency:.2f}s")
        m2.metric("Speed", f"{tps:.0f} t/s")
    
    return {
        "name": model_name,
        "content": content,
        "latency": latency,
        "tps": tps,
        "placeholder": placeholder
    }

async def run_evaluation_stream(prompt, placeholders, metrics_placeholders):
    tasks = []
    for (name, id), ph, m_ph in zip(models.items(), placeholders, metrics_placeholders):
        tasks.append(fetch_response_stream(name, id, prompt, ph, m_ph))
    return await asyncio.gather(*tasks)

if st.button("🚀 Run Model Routing Analysis"):
    if not prompt.strip():
        st.warning("Please enter a prompt to evaluate.")
    else:
        st.markdown("---")
        st.subheader("📊 Live Routing Intelligence")
        
        # Pre-create UI containers for side-by-side streaming
        cols = st.columns(len(models))
        placeholders = []
        metrics_placeholders = []
        
        for i, (name, _) in enumerate(models.items()):
            with cols[i]:
                st.markdown(f"### 🤖 {name}")
                # Create empty containers to be filled during stream
                metrics_placeholders.append(st.empty()) 
                placeholders.append(st.empty())
                
        # Run async stream
        results = asyncio.run(run_evaluation_stream(prompt, placeholders, metrics_placeholders))
        
        # Highlight winner after finish
        fastest_model = max(results, key=lambda x: x['tps'])
        
        for result in results:
            if result['name'] == fastest_model['name']:
                result['placeholder'].markdown(f"<div class='winner-card'><div class='response-box'>{result['content']}</div></div>", unsafe_allow_html=True)
        
        st.success(f"**Routing Recommendation:** **{fastest_model['name']}** provided the highest throughput at **{fastest_model['tps']:.0f} tokens/sec**. If quality is acceptable, route production traffic to this model.")
