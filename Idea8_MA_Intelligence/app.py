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

class AuditRequest(BaseModel):
    company_data: str

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
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/audit")
async def audit(req: AuditRequest):
    print(f"💰 Deploying M&A Intelligence Swarm...")
    
    sys_prompt = """You are a Senior M&A Auditor. Analyze the provided company data for an acquisition.
    1. Identify 4 critical 'Red Flags' (Financial, Legal, or Cultural).
    2. Provide scores (0-100) for: Financial Health, Market Fit, Team Strength, and Legal Compliance.
    3. Final recommendation: BUY, HOLD, or PASS with a brief justification.
    
    Return ONLY a JSON object:
    {
      "red_flags": [{"title": "...", "severity": "HIGH/MED", "impact": "..."}],
      "radar_stats": [80, 60, 70, 90],
      "recommendation": {"decision": "...", "justification": "...", "confidence": 1-100}
    }"""
    
    res_raw = await call_agent(sys_prompt, req.company_data)
    try:
        data = json.loads(clean_json(res_raw))
        return data
    except:
        return {"error": "Intelligence scan failed."}
