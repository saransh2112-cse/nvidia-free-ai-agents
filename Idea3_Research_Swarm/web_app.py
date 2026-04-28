import streamlit as st
import asyncio
import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

st.set_page_config(
    page_title="NVIDIA Research Swarm",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .main-title {
        background: linear-gradient(90deg, #76b900, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .agent-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(118, 185, 0, 0.3);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .agent-card:hover {
        transform: translateY(-5px);
        border-color: #76b900;
        box-shadow: 0 0 20px rgba(118, 185, 0, 0.2);
    }
    .report-container {
        background: rgba(15, 23, 42, 0.8);
        padding: 40px;
        border-radius: 16px;
        border: 1px solid #38bdf8;
        margin-top: 30px;
        box-shadow: 0 0 40px rgba(56, 189, 248, 0.1);
        max-height: 500px;
        overflow-y: auto;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #76b900, #5da000);
        color: white;
        font-weight: 800;
        border-radius: 8px;
        border: none;
        padding: 12px 30px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(118, 185, 0, 0.4);
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(118, 185, 0, 0.6);
        color: white;
    }
    /* Streaming text style */
    .stream-text {
        font-size: 1rem;
        line-height: 1.6;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
if not api_key or api_key == "your_api_key_here":
    st.error("Please set your NVIDIA_API_KEY in the .env file")
    st.stop()

client = AsyncOpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=api_key
)

PLANNER_MODEL = "meta/llama-3.1-8b-instruct"
WRITER_MODEL = "meta/llama-3.1-8b-instruct"

async def generate_outline(topic):
    prompt = f"""
    You are an expert technical planner. 
    Topic: {topic}
    Generate a JSON array of 3 distinct sub-topics that need to be covered to explain this topic comprehensively.
    Return ONLY a valid JSON array of strings, without any markdown formatting, backticks, or extra text.
    Example: ["Introduction to X", "Core Concepts", "Real-world Applications"]
    """
    
    response = await client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    
    content = response.choices[0].message.content.strip()
    try:
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        outline = json.loads(content)
        return outline[:3]
    except Exception as e:
        return ["Introduction", "Core Architecture", "Future Implications"]

async def write_section(topic, section_title, status_placeholder, text_placeholder):
    prompt = f"""
    You are an expert technical writer creating a section for a comprehensive guide on "{topic}".
    Write the section titled "{section_title}".
    Provide detailed, professional, and engaging content. Use markdown formatting.
    Do not write the overall introduction or conclusion, just focus purely on this specific section.
    Limit the response to 3-4 paragraphs.
    """
    
    try:
        status_placeholder.info(f"Agent researching...")
        response = await client.chat.completions.create(
            model=WRITER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        content = ""
        async for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content is not None:
                    content += delta.content
                    # Stream the text into the column
                    text_placeholder.markdown(f'<div class="stream-text">{content}▌</div>', unsafe_allow_html=True)
                    await asyncio.sleep(0.01) # Small sleep to yield to event loop
                
        # Final render without the cursor
        text_placeholder.markdown(f'<div class="stream-text">{content}</div>', unsafe_allow_html=True)
        status_placeholder.success(f"✔ Completed!")
        return f"{content}\n\n"
        
    except Exception as e:
        status_placeholder.error(f"Error")
        return f"## {section_title}\n\nError generating content: {e}\n\n"

st.markdown('<p class="main-title">🐝 The Asynchronous Swarm</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Powered by NVIDIA NIMs (Llama 3.1 8B) running in parallel.</p>', unsafe_allow_html=True)

topic = st.text_input("What should the Swarm research?", value="The Future of Autonomous Multi-Agent Systems")

if st.button("🚀 Deploy Swarm"):
    st.session_state['report'] = None
    
    st.markdown("### 🧠 Phase 1: Generating Architecture")
    with st.status(f"Planner Agent ({PLANNER_MODEL}) is thinking...", expanded=True) as status:
        outline = asyncio.run(generate_outline(topic))
        status.update(label="Outline Generated Successfully!", state="complete", expanded=False)
        
    st.success(f"**Generated Topics:** {', '.join(outline)}")
    
    st.markdown("### ⚡ Phase 2: Concurrent Swarm Execution")
    
    cols = st.columns(len(outline))
    status_placeholders = []
    text_placeholders = []
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f'<div class="agent-card"><h3 style="color:#76b900;margin:0;font-size:1.2rem;">Agent {i+1}</h3><p style="margin:0;color:#cbd5e1;font-size:0.9rem;">{outline[i]}</p></div>', unsafe_allow_html=True)
            status_ph = st.empty()
            text_ph = st.empty()
            status_placeholders.append(status_ph)
            text_placeholders.append(text_ph)

    async def run_writers(outline, status_phs, text_phs):
        tasks = [write_section(topic, section, s_ph, t_ph) for section, s_ph, t_ph in zip(outline, status_phs, text_phs)]
        return await asyncio.gather(*tasks)

    sections = asyncio.run(run_writers(outline, status_placeholders, text_placeholders))
    
    st.balloons()
    
    report = f"# Comprehensive Guide: {topic}\n\n"
    for section in sections:
        report += section
        
    st.session_state['report'] = report

if 'report' in st.session_state and st.session_state['report']:
    st.markdown("### 📑 Phase 3: Compiled Output")
    
    # Use native Streamlit container with fixed height for a scrollable box!
    with st.container(height=600):
        st.markdown(st.session_state['report'])
        
    st.download_button(
        label="⬇️ Download Markdown Report",
        data=st.session_state['report'],
        file_name=f"{topic.replace(' ', '_')}_Report.md",
        mime="text/markdown"
    )
