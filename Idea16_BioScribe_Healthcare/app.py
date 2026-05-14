import os, json, asyncio, re
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

client = AsyncOpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
MODEL = "meta/llama-3.1-8b-instruct"

class PatientRequest(BaseModel):
    patient_data: str # Symptoms, age, history

# ─── Swarm Agents ─────────────────────────────────────────────────────
AGENTS = [
    {
        "role": "TRIAGE",
        "name": "Triage Medic",
        "icon": "🩺",
        "color": "#3b82f6",
    },
    {
        "role": "PROTOCOL",
        "name": "Protocol Expert",
        "icon": "📜",
        "color": "#06b6d4",
    },
    {
        "role": "MATCHER",
        "name": "Trial Matcher",
        "icon": "🧪",
        "color": "#a855f7",
    },
    {
        "role": "BRIEF",
        "name": "Doctor's Brief",
        "icon": "📝",
        "color": "#10b981",
    }
]

AGENT_PROMPTS = {
    "TRIAGE": """You are an Emergency Triage Medic.
Analyze the patient symptoms and medical history.
1. Identify the core symptoms.
2. Determine Urgency Level (Emergency / Urgent / Routine).
3. Suggest the most likely medical department.
Be precise and clinical. Under 120 words.
End with: URGENCY: EMERGENCY / URGENT / ROUTINE
Then: SCORE: [0-10] (Severity)""",

    "PROTOCOL": """You are a Medical Protocol Expert.
Cross-reference the patient's symptoms with standard healthcare protocols.
1. List 3 immediate diagnostic questions for the doctor to ask.
2. Identify potential red flags (contraindications).
3. Suggest a primary test (e.g., Blood work, MRI, ECG).
Under 120 words.
End with: PROTOCOL: [Specific Protocol Name]""",

    "MATCHER": """You are a Clinical Trial Matcher.
Analyze the patient's condition and match them to potential active clinical trials.
1. Name a relevant clinical trial type.
2. State the eligibility match score (0-100%).
3. Identify a potential benefit of participation.
Be specific. Under 120 words.
End with: TRIAL STATUS: MATCH FOUND / NO MATCH / RE-SCREEN""",

    "BRIEF": """You are a Clinical Scribe writing a brief for a busy doctor.
Synthesize the findings from triage, protocols, and trials into a 10-second briefing.
1. Patient Summary (one line).
2. Key action to take in the first 5 minutes.
3. Recommended next step.
Keep it direct and high-stakes. Under 130 words.
End with: ACTION: IMMEDIATE / FOLLOW-UP / MONITOR""",
}

async def run_agent(agent: dict, req: PatientRequest) -> dict:
    prompt_ctx = f"PATIENT DATA:\n{req.patient_data}"
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": AGENT_PROMPTS[agent["role"]]},
                {"role": "user", "content": prompt_ctx},
            ],
            temperature=0.3,
            max_tokens=250,
        )
        analysis = response.choices[0].message.content.strip()
        # Clean markdown
        analysis = re.sub(r'\*\*(.+?)\*\*', r'\1', analysis)
        analysis = re.sub(r'\*+', '', analysis).strip()

        verdict = ""
        for line in reversed(analysis.split("\n")):
            line = line.strip()
            if line and ":" in line:
                verdict = line.split(":", 1)[-1].strip()
                break

        return {**agent, "analysis": analysis, "verdict": verdict}
    except Exception as e:
        return {**agent, "analysis": f"Agent offline: {e}", "verdict": "OFFLINE"}

# ─── Routes ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/triage")
async def triage(req: PatientRequest):
    print(f"🏥 Bio-Scribe deploying for triage...")
    agent_results = await asyncio.gather(
        *[run_agent(a, req) for a in AGENTS]
    )
    return {"agents": list(agent_results)}
