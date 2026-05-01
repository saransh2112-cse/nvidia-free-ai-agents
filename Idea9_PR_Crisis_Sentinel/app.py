import os
import json
import asyncio
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

app = FastAPI()

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

MODEL = "meta/llama-3.1-8b-instruct"

class CrisisRequest(BaseModel):
    crisis_text: str

def clean_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match: return text
        content = match.group(0)
        # Fix unescaped newlines in strings
        def replace_newlines(m):
            return m.group(0).replace('\n', '\\n')
        content = re.sub(r'":\s*"(.*?)"', replace_newlines, content, flags=re.DOTALL)
        return content
    except: return text

async def call_agent(system_prompt: str, user_prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/crisis")
async def crisis(req: CrisisRequest):
    print(f"🔥 Deploying PR Sentinel Swarm...")
    
    sys_prompt = """You are a Crisis Communication Master. Analyze the provided PR crisis.
    1. Identify 3 'Outrage Hotspots' (e.g. Platform, Core Concern, Sentiment).
    2. Generate 2 competing strategies:
       - 'The Peacekeeper': Empathy-led, apologetic.
       - 'The Defender': Logical, brand-first, corrective.
    3. Calculate the 'Trust Capital at Risk' (0-100%).
    
    Return ONLY a JSON object:
    {
      "hotspots": [{"area": "...", "sentiment": "...", "severity": "CRITICAL/HIGH"}],
      "strategies": {
        "peacekeeper": {"title": "...", "body": "...", "impact": "..."},
        "defender": {"title": "...", "body": "...", "impact": "..."}
      },
      "trust_score": 35
    }"""
    
    res_raw = await call_agent(sys_prompt, req.crisis_text)
    try:
        data = json.loads(clean_json(res_raw))
        return data
    except Exception as e:
        return {"error": f"Sentinel scan failed: {str(e)}", "raw": res_raw}
