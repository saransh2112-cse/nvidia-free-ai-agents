import os, json, asyncio, re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

from pathlib import Path

# Load .env from root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("NVIDIA_API_KEY")

app = FastAPI()
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
MODEL = "meta/llama-3.1-8b-instruct"

# ─── Request Model ────────────────────────────────────────────────────
class EchoRequest(BaseModel):
    company: str           # e.g., "Acme SaaS"
    plan: str              # e.g., "Pro - $299/mo"
    tenure_months: int     # e.g., 14
    usage_trend: str       # e.g., "Dropped 60% in last 30 days"
    support_tickets: str   # e.g., "3 unresolved tickets in 2 weeks"
    billing_signals: str   # e.g., "Downgrade request submitted"
    industry: str          # e.g., "E-commerce"

# ─── Agent Configurations ─────────────────────────────────────────────
AGENTS = [
    {
        "role": "SIGNAL_ANALYST",
        "name": "Churn Signal Analyst",
        "icon": "📉",
        "color": "#ef4444",
        "focus": "behavioral analytics, usage pattern decay, engagement scoring, churn probability modeling",
    },
    {
        "role": "ROOT_CAUSE",
        "name": "Root Cause Detective",
        "icon": "🔍",
        "color": "#f97316",
        "focus": "customer psychology, pain point diagnosis, friction identification, competitive displacement",
    },
    {
        "role": "RETENTION_ARCHITECT",
        "name": "Retention Offer Architect",
        "icon": "💌",
        "color": "#a855f7",
        "focus": "personalized retention offers, discount strategy, feature unlocks, loyalty incentives",
    },
    {
        "role": "CS_BRIEF",
        "name": "Customer Success Brief",
        "icon": "📋",
        "color": "#06b6d4",
        "focus": "CS team action plans, outreach scripts, escalation protocols, win-back playbooks",
    },
]

AGENT_PROMPTS = {
    "SIGNAL_ANALYST": """You are a world-class Churn Signal Analyst for a SaaS company.
Analyze the customer signals and calculate a churn risk score (0-100).
Break down: usage decay severity, support friction score, billing intent signal.
Be specific with numbers. Under 120 words.
End with: CHURN RISK: CRITICAL (80-100) / HIGH (60-79) / MODERATE (40-59) / LOW (<40)
Then: SCORE: [number]/100""",

    "ROOT_CAUSE": """You are a Customer Psychology expert and Root Cause Detective.
Given these churn signals, diagnose the PRIMARY reason this customer is leaving.
Identify: main pain point, moment of disillusionment, likely competitor they're moving to.
Be direct and specific. Under 120 words.
End with: ROOT CAUSE: [one-line diagnosis]""",

    "RETENTION_ARCHITECT": """You are a Revenue Retention specialist at a top SaaS company.
Design a personalized retention offer for this at-risk customer.
Include: specific discount %, feature unlock, success milestone offer, or executive outreach.
Make it feel personal, not generic. Under 130 words.
End with: OFFER TYPE: DISCOUNT / FEATURE UNLOCK / EXECUTIVE OUTREACH / HYBRID""",

    "CS_BRIEF": """You are a Customer Success Team Lead writing an action brief.
Write a clear playbook for the CS rep who will contact this customer TODAY.
Include: opening line, 2 key talking points, one question to ask, and the offer to present.
Keep it actionable, not corporate. Under 130 words.
End with: PRIORITY: URGENT / HIGH / STANDARD""",
}

async def run_agent(agent: dict, req: EchoRequest) -> dict:
    system_prompt = AGENT_PROMPTS[agent["role"]]
    user_prompt = f"""CUSTOMER PROFILE:
Company: {req.company}
Current Plan: {req.plan}
Tenure: {req.tenure_months} months
Industry: {req.industry}

CHURN SIGNALS:
Usage Trend: {req.usage_trend}
Support Tickets: {req.support_tickets}
Billing Signals: {req.billing_signals}

Deliver your expert analysis now."""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=220,
        )
        analysis = response.choices[0].message.content.strip()
        # ── Strip markdown asterisks from LLM output ──
        analysis = re.sub(r'\*\*(.+?)\*\*', r'\1', analysis)
        analysis = re.sub(r'\*+', '', analysis).strip()

        verdict = "UNKNOWN"
        for line in reversed(analysis.split("\n")):
            line = line.strip()
            if line and ":" in line:
                verdict = line.split(":", 1)[-1].strip()
                break

        # Extract numeric score if present
        score = None
        for line in analysis.split("\n"):
            if "SCORE:" in line.upper():
                try:
                    score = int(''.join(filter(str.isdigit, line.split(":")[-1].split("/")[0])))
                except Exception:
                    pass

        return {**agent, "analysis": analysis, "verdict": verdict, "score": score}
    except Exception as e:
        return {**agent, "analysis": f"Agent offline: {e}", "verdict": "OFFLINE", "score": None}

# ─── Routes ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/echo")
async def echo(req: EchoRequest):
    print(f"📉 Echo activated for: {req.company} | Plan: {req.plan}")

    agent_results = await asyncio.gather(
        *[run_agent(a, req) for a in AGENTS]
    )

    # Extract overall churn score
    churn_score = 50
    for a in agent_results:
        if a.get("score") is not None:
            churn_score = a["score"]
            break

    if churn_score >= 80:
        risk_level = "CRITICAL"
        risk_color = "#ef4444"
    elif churn_score >= 60:
        risk_level = "HIGH"
        risk_color = "#f97316"
    elif churn_score >= 40:
        risk_level = "MODERATE"
        risk_color = "#eab308"
    else:
        risk_level = "LOW"
        risk_color = "#22c55e"

    return {
        "company": req.company,
        "plan": req.plan,
        "tenure_months": req.tenure_months,
        "industry": req.industry,
        "agents": list(agent_results),
        "churn_score": churn_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
    }
