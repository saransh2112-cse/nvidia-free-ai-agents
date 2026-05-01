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

# Dual-Agent Swarm - Optimized for Instant Demo Speed
AUDITOR_MODEL = "meta/llama-3.1-8b-instruct"
NEGOTIATOR_MODEL = "meta/llama-3.1-8b-instruct"

class ContractRequest(BaseModel):
    contract_text: str

def clean_json(text):
    """Robustly extract JSON from a string."""
    try:
        # Find the first { and the last }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    except:
        return text

async def call_agent(model: str, system_prompt: str, user_prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Agent Error ({model}): {e}")
        return ""

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/negotiate")
async def negotiate(req: ContractRequest):
    print(f"⚖️ Deploying Legal Swarm...")

    # Phase 1: Llama 8B Audits for Risks
    auditor_sys = """You are a Senior Legal Auditor. Identify 3-5 high-risk clauses.
    Focus on: Indemnification, Liability caps, Termination rights.
    Return ONLY a JSON object: {"risks": [{"clause_name": "...", "original_text": "...", "risk_score": 1-100, "explanation": "..."}]}"""
    
    audit_res_raw = await call_agent(AUDITOR_MODEL, auditor_sys, req.contract_text)
    try:
        audit_data = json.loads(clean_json(audit_res_raw))
    except Exception as e:
        print(f"Audit Parse Error: {e}")
        return {"error": "Audit failed."}

    # Phase 2: Llama 70B Negotiates
    negotiator_sys = """You are a Master Negotiator. For these risks, draft counter-offers.
    Provide a brief 'Negotiation Duel' log.
    Return ONLY a JSON object: {"negotiations": [{"risk_name": "...", "counter_offer": "...", "duel_log": [{"agent": "Opponent", "msg": "..."}, {"agent": "Llama-70B", "msg": "..."}]}], "score": 85}"""
    
    neg_res_raw = await call_agent(NEGOTIATOR_MODEL, negotiator_sys, json.dumps(audit_data))
    try:
        neg_data = json.loads(clean_json(neg_res_raw))
    except Exception as e:
        print(f"Negotiation Parse Error: {e}")
        return {"error": "Negotiation failed."}

    return {
        "risks": audit_data.get("risks", []),
        "negotiations": neg_data.get("negotiations", []),
        "score": neg_data.get("score", 0)
    }
