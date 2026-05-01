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

class RevenueRequest(BaseModel):
    market_data: str

def clean_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match: return text
        content = match.group(0)
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
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/revenue")
async def revenue(req: RevenueRequest):
    print(f"💰 Activating Midas Revenue Swarm...")
    
    sys_prompt = """You are a Revenue Operations Genius. Analyze the provided market/competitor data.
    1. Identify 3 'Pricing Arbitrage' opportunities (where to raise/lower prices).
    2. Provide a 'Profit Forecast' (estimated revenue lift in %).
    3. Generate 2 'Flash Offer' headlines & descriptions to capture the opportunity.
    
    Return ONLY a JSON object:
    {
      "arbitrage": [{"product": "...", "action": "...", "reason": "..."}],
      "forecast": 25,
      "flash_offers": [
        {"headline": "...", "description": "..."}
      ]
    }"""
    
    res_raw = await call_agent(sys_prompt, req.market_data)
    try:
        data = json.loads(clean_json(res_raw))
        return data
    except Exception as e:
        return {"error": f"Midas scan failed: {str(e)}", "raw": res_raw}
