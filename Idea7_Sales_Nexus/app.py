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

class ProspectRequest(BaseModel):
    target_data: str

def clean_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match: return match.group(0)
        return text
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

@app.post("/prospect")
async def prospect(req: ProspectRequest):
    print(f"📡 Initializing Nexus Infiltration...")
    
    sys_prompt = """You are a Master Sales Psychologist. Analyze the provided digital footprint of a prospect.
    1. Identify 3 key research points (recent wins, pain points, or interests).
    2. Map their personality (Analytical, Visionary, or Driver).
    3. Generate 2 hyper-personalized pitch options.
    
    Return ONLY a JSON object:
    {
      "research": [{"topic": "...", "insight": "..."}],
      "personality": {"type": "...", "traits": ["...", "..."], "score": 1-100},
      "pitches": [
        {"subject": "...", "body": "..."}
      ]
    }"""
    
    res_raw = await call_agent(sys_prompt, req.target_data)
    try:
        data = json.loads(clean_json(res_raw))
        return data
    except:
        return {"error": "Nexus scan failed to parse."}
