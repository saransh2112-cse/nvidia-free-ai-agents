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
class VertexRequest(BaseModel):
    name: str               # e.g., "Sarah Chen"
    role: str               # e.g., "Senior Software Engineer"
    department: str         # e.g., "Engineering"
    tenure_years: float     # e.g., 3.5
    current_salary: int     # e.g., 120000
    location: str           # e.g., "San Francisco, CA"
    recent_signals: str     # e.g., "Updated LinkedIn, missed 2 team events, asked about PTO policy"
    performance: str        # e.g., "Top 10% performer, promoted 6 months ago"
    last_raise_months: int  # e.g., 18

# ─── Agent Configurations ─────────────────────────────────────────────
AGENTS = [
    {
        "role": "SALARY_BENCHMARKER",
        "name": "Market Salary Benchmarker",
        "icon": "💰",
        "color": "#22c55e",
        "focus": "compensation benchmarking, market pay rates, total compensation analysis, equity gaps",
    },
    {
        "role": "FLIGHT_PROFILER",
        "name": "Flight Risk Profiler",
        "icon": "🎯",
        "color": "#ef4444",
        "focus": "behavioral flight risk signals, career stagnation, engagement decay, attrition psychology",
    },
    {
        "role": "RETENTION_ARCHITECT",
        "name": "Retention Package Architect",
        "icon": "🎁",
        "color": "#a855f7",
        "focus": "personalized retention packages, career pathing, equity refresh, role expansion, recognition",
    },
    {
        "role": "HR_BRIEF",
        "name": "HR Executive Brief",
        "icon": "📋",
        "color": "#f59e0b",
        "focus": "manager action plans, stay interview scripts, HR escalation, executive sponsorship",
    },
]

AGENT_PROMPTS = {
    "SALARY_BENCHMARKER": """You are a Compensation Intelligence expert with access to market data.
Benchmark this employee's salary against current market rates for their role and location.
Estimate: market median, top 25th percentile, and the compensation gap (if any).
Use realistic numbers based on current tech market. Under 120 words.
End with: COMP STATUS: UNDERPAID / MARKET RATE / ABOVE MARKET
Then: GAP: $[amount] below market (or AT MARKET)""",

    "FLIGHT_PROFILER": """You are a Talent Retention psychologist specializing in flight risk.
Analyze the employee's behavioral signals and calculate a flight risk score (0-100).
Identify the top 2 risk factors driving their likelihood to leave.
Be specific and honest. Under 120 words.
End with: FLIGHT RISK: CRITICAL (80-100) / HIGH (60-79) / MODERATE (40-59) / LOW (<40)
Then: SCORE: [number]/100""",

    "RETENTION_ARCHITECT": """You are a Head of People at a top tech company.
Design a personalized retention package for this employee.
Include: salary adjustment recommendation, equity/bonus component, career growth offer, and one unique non-monetary perk.
Make it feel genuinely personalized. Under 130 words.
End with: PACKAGE TYPE: COMPENSATION / EQUITY / CAREER PATH / HYBRID""",

    "HR_BRIEF": """You are an HR Business Partner writing an urgent action brief.
Write a clear action plan for the manager to execute THIS WEEK.
Include: conversation opener, 2 key questions to ask in a stay interview, what to offer, and escalation trigger.
Keep it human, not corporate speak. Under 130 words.
End with: ACTION: IMMEDIATE / THIS WEEK / MONITOR""",
}

async def run_agent(agent: dict, req: VertexRequest) -> dict:
    system_prompt = AGENT_PROMPTS[agent["role"]]
    user_prompt = f"""EMPLOYEE PROFILE:
Name: {req.name}
Role: {req.role}
Department: {req.department}
Tenure: {req.tenure_years} years
Current Salary: ${req.current_salary:,}/year
Location: {req.location}
Performance: {req.performance}
Last Raise: {req.last_raise_months} months ago

FLIGHT RISK SIGNALS:
{req.recent_signals}

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

@app.post("/vertex")
async def vertex(req: VertexRequest):
    print(f"🎯 Vertex activated for: {req.name} | Role: {req.role}")

    agent_results = await asyncio.gather(
        *[run_agent(a, req) for a in AGENTS]
    )

    # Extract flight risk score
    flight_score = 50
    for a in agent_results:
        if a.get("score") is not None:
            flight_score = a["score"]
            break

    if flight_score >= 80:
        risk_level = "CRITICAL"
        risk_color = "#ef4444"
    elif flight_score >= 60:
        risk_level = "HIGH"
        risk_color = "#f97316"
    elif flight_score >= 40:
        risk_level = "MODERATE"
        risk_color = "#eab308"
    else:
        risk_level = "LOW"
        risk_color = "#22c55e"

    return {
        "name": req.name,
        "role": req.role,
        "department": req.department,
        "tenure_years": req.tenure_years,
        "location": req.location,
        "agents": list(agent_results),
        "flight_score": flight_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
    }
