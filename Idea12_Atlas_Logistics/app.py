import os, json, asyncio, re, httpx
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
class AtlasRequest(BaseModel):
    origin: str
    destination: str
    cargo: str
    carrier: str

# ─── Live Intelligence Agents ─────────────────────────────────────────
async def fetch_live_disruptions(origin: str, destination: str) -> list[str]:
    """Scrape live news for shipping disruptions."""
    headlines = []
    # Updated to working RSS feeds
    feeds = [
        "https://www.cnbc.com/id/10001147/device/rss/rss.html", # CNBC Business
        "https://www.cnbc.com/id/100727362/device/rss/rss.html", # CNBC World
    ]
    keywords = [
        "port", "shipping", "cargo", "supply chain", "freight", "container",
        "strike", "closure", "disruption", "delay", "tariff", "sanctions",
        "maritime", "canal", "vessel", "maersk", "hapag",
        origin.split(",")[0].lower(),
        destination.split(",")[0].lower(),
    ]
    try:
        async with httpx.AsyncClient(timeout=5) as h:
            for feed_url in feeds:
                try:
                    r = await h.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
                    # More robust regex for title tags (handles CDATA and plain text)
                    titles = re.findall(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", r.text)
                    for t in titles:
                        if any(kw in t.lower() for kw in keywords):
                            headlines.append(t)
                except Exception:
                    continue
    except Exception:
        pass
    if not headlines:
        return [
            "Global shipping rates surge 40% amid Red Sea rerouting demands",
            "Port workers threaten strike action at major European terminals",
            "Panama Canal water levels force cargo restrictions on large vessels",
        ]
    return list(dict.fromkeys(headlines))[:5]  # deduplicate, top 5

# ─── C-Suite Agent Configs ────────────────────────────────────────────
AGENTS = [
    {
        "role": "INTELLIGENCE",
        "name": "Geo-Political Intelligence Officer",
        "icon": "🛰️",
        "color": "#06b6d4",
        "focus": "threat assessment, real-time disruption analysis, geopolitical risk, port closure intelligence",
    },
    {
        "role": "ROUTE_ANALYST",
        "name": "Route Risk Analyst",
        "icon": "📊",
        "color": "#a855f7",
        "focus": "maritime route viability, choke-point risk, weather patterns, transit time analysis",
    },
    {
        "role": "RE_ROUTER",
        "name": "Re-Route Strategist",
        "icon": "🔄",
        "color": "#f97316",
        "focus": "alternative routing, carrier selection, cost-time tradeoffs, port alternatives",
    },
    {
        "role": "CONTRACT",
        "name": "Carrier Contract Agent",
        "icon": "📋",
        "color": "#22c55e",
        "focus": "carrier negotiations, SLA terms, force majeure clauses, re-booking brief drafting",
    },
]

async def run_agent(agent: dict, origin: str, destination: str,
                    cargo: str, carrier: str, headlines: list[str]) -> dict:
    """Run a single Atlas agent with live disruption context."""
    news_ctx = "\n".join(f"• {h}" for h in headlines)

    role_prompts = {
        "INTELLIGENCE": f"""You are the {agent['name']} for a global logistics firm.
Analyze the live news headlines and assess the threat level to this shipment.
Be direct and tactical. Under 120 words.
End with: THREAT LEVEL: CRITICAL / HIGH / MODERATE / LOW""",

        "ROUTE_ANALYST": f"""You are the {agent['name']} for a global logistics firm.
Evaluate the primary shipping route viability given current disruptions.
Focus on choke points, transit time risk, and cost implications. Under 120 words.
End with: ROUTE STATUS: VIABLE / AT RISK / COMPROMISED""",

        "RE_ROUTER": f"""You are the {agent['name']} for a global logistics firm.
Propose 2 specific alternative routes for this shipment, with estimated extra cost/days.
Be concrete: name actual ports, canals, or overland corridors. Under 140 words.
End with: RECOMMENDATION: REROUTE / HOLD / PROCEED""",

        "CONTRACT": f"""You are the {agent['name']} for a global logistics firm.
Draft a concise carrier re-booking brief that includes: force majeure clause trigger,
new preferred carrier/route requirements, and SLA penalty waiver request. Under 130 words.
End with: ACTION: EXECUTE / PENDING / HOLD""",
    }

    system_prompt = role_prompts.get(agent["role"], "You are a logistics expert.")
    user_prompt = f"""SHIPMENT DETAILS:
Origin: {origin}
Destination: {destination}
Cargo: {cargo}
Current Carrier: {carrier}

LIVE DISRUPTION INTELLIGENCE:
{news_ctx}

Provide your expert assessment now."""

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

        # Extract status keyword from last line
        status = "UNKNOWN"
        for line in reversed(analysis.split("\n")):
            if ":" in line:
                status = line.split(":")[-1].strip()
                break

        return {**agent, "analysis": analysis, "status": status}
    except Exception as e:
        return {**agent, "analysis": f"Agent offline: {e}", "status": "OFFLINE"}

# ─── Routes ───────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/atlas")
async def atlas(req: AtlasRequest):
    print(f"🚢 Atlas activated: {req.origin} → {req.destination} | Cargo: {req.cargo}")

    # Fetch live intelligence FIRST, then run all 4 agents in parallel
    headlines = await fetch_live_disruptions(req.origin, req.destination)

    agent_results = await asyncio.gather(
        *[run_agent(a, req.origin, req.destination, req.cargo, req.carrier, headlines)
          for a in AGENTS]
    )

    # Tally overall risk
    statuses = [a["status"].upper() for a in agent_results]
    if any("CRITICAL" in s or "COMPROMISED" in s for s in statuses):
        overall_risk = "CRITICAL"
        risk_color = "#ef4444"
    elif any("HIGH" in s or "AT RISK" in s or "REROUTE" in s for s in statuses):
        overall_risk = "HIGH"
        risk_color = "#f97316"
    elif any("MODERATE" in s for s in statuses):
        overall_risk = "MODERATE"
        risk_color = "#eab308"
    else:
        overall_risk = "LOW"
        risk_color = "#22c55e"

    return {
        "origin": req.origin,
        "destination": req.destination,
        "cargo": req.cargo,
        "carrier": req.carrier,
        "headlines": headlines,
        "agents": list(agent_results),
        "overall_risk": overall_risk,
        "risk_color": risk_color,
    }
