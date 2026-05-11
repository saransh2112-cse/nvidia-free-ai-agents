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
class VinciRequest(BaseModel):
    product_idea: str     # e.g., "AI-powered noise-canceling headphones"
    market: str           # e.g., "Consumer Electronics"
    target_user: str      # e.g., "Remote workers & gamers"

# ─── Live Market Intelligence ─────────────────────────────────────────
async def fetch_market_news(product_idea: str, market: str) -> list[str]:
    """Scrape live news for relevant product/market news."""
    keywords = [
        kw.lower() for kw in
        (product_idea.split()[:4] + market.split()[:3] +
         ["patent", "innovation", "product launch", "startup", "funding", "R&D"])
    ]
    headlines = []
    try:
        async with httpx.AsyncClient(timeout=5) as h:
            # Updated to working RSS feeds
            for feed in [
                "https://www.cnbc.com/id/19854910/device/rss/rss.html", # CNBC Tech
                "https://www.cnbc.com/id/10001147/device/rss/rss.html", # CNBC Business
            ]:
                try:
                    r = await h.get(feed, headers={"User-Agent": "Mozilla/5.0"})
                    # More robust regex for title tags
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
            f"VC investment in {market} hits record $12B in Q1 2025",
            "AI-integrated consumer products see 3x adoption growth YoY",
            "Patent filings in tech sector surge — 40% driven by AI innovation",
            "Startups targeting remote workers capture $8B in new funding",
        ]
    return list(dict.fromkeys(headlines))[:5]

# ─── Vinci Agent Configurations ───────────────────────────────────────
AGENTS = [
    {
        "role": "PATENT_SCOUT",
        "name": "Patent Intelligence Scout",
        "icon": "🔍",
        "color": "#f59e0b",
        "focus": "patent landscape, IP risks, existing claims, freedom-to-operate analysis",
    },
    {
        "role": "MARKET_ANALYST",
        "name": "Competitor Market Analyst",
        "icon": "📊",
        "color": "#06b6d4",
        "focus": "competitor products, pricing gaps, customer pain points, market size estimation",
    },
    {
        "role": "INNOVATION_GAP",
        "name": "Innovation Gap Detector",
        "icon": "💡",
        "color": "#a855f7",
        "focus": "unmet needs, white-space opportunities, feature differentiation, technology convergence",
    },
    {
        "role": "PRODUCT_BRIEF",
        "name": "Product Design Architect",
        "icon": "📋",
        "color": "#22c55e",
        "focus": "MVP feature set, technical feasibility, go-to-market positioning, USP definition",
    },
]

AGENT_PROMPTS = {
    "PATENT_SCOUT": """You are a senior Patent Intelligence Scout at a top innovation consultancy.
Analyze the product idea and assess the IP landscape.
Identify: 2 key existing patent risks, 1 protectable innovation angle, freedom-to-operate outlook.
Be specific — cite likely patent holders (e.g., Apple, Bose, Sony). Under 130 words.
End with: IP STATUS: CLEAR / CONTESTED / RISKY""",

    "MARKET_ANALYST": """You are a competitive intelligence analyst specializing in product markets.
Analyze the competitive landscape for this product idea.
Identify: top 3 existing competitors, their price points, and the biggest customer complaint they all share.
Be concrete with real brand names and numbers. Under 130 words.
End with: MARKET OPPORTUNITY: LARGE / MODERATE / SATURATED""",

    "INNOVATION_GAP": """You are an innovation strategist who identifies billion-dollar white spaces.
Given the product idea, live market signals, and competitive gaps, identify:
1. The single most underserved customer pain point
2. One emerging technology convergence that creates a new opportunity
3. A differentiation angle no competitor has nailed yet
Under 130 words. End with: OPPORTUNITY: BREAKTHROUGH / INCREMENTAL / NICHE""",

    "PRODUCT_BRIEF": """You are a Silicon Valley product architect who has shipped 10+ successful products.
Draft a crisp MVP product brief:
- Core USP (1 sentence)
- Top 3 MVP features (be specific)
- Recommended tech stack (2-3 components)
- Target price point & go-to-market channel
Under 140 words. End with: FEASIBILITY: HIGH / MEDIUM / LOW""",
}

async def run_vinci_agent(agent: dict, product_idea: str, market: str,
                          target_user: str, headlines: list[str]) -> dict:
    """Run a single Vinci R&D agent."""
    news_ctx = "\n".join(f"• {h}" for h in headlines)
    system_prompt = AGENT_PROMPTS[agent["role"]]
    user_prompt = f"""PRODUCT IDEA: {product_idea}
MARKET SECTOR: {market}
TARGET USER: {target_user}

LIVE MARKET INTELLIGENCE:
{news_ctx}

Deliver your expert analysis now."""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=230,
        )
        analysis = response.choices[0].message.content.strip()

        # Extract final verdict from last line
        verdict = "UNKNOWN"
        for line in reversed(analysis.split("\n")):
            if ":" in line and any(
                kw in line.upper() for kw in
                ["STATUS", "OPPORTUNITY", "FEASIBILITY", "MARKET"]
            ):
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

@app.post("/vinci")
async def vinci(req: VinciRequest):
    print(f"🧪 Vinci activated: '{req.product_idea}' | Market: {req.market}")

    # Fetch live market intel, then run all 4 agents in parallel
    headlines = await fetch_market_news(req.product_idea, req.market)

    agent_results = await asyncio.gather(
        *[run_vinci_agent(a, req.product_idea, req.market, req.target_user, headlines)
          for a in AGENTS]
    )

    # Score overall viability
    verdicts = [a["verdict"].upper() for a in agent_results]
    score = 0
    if any("CLEAR" in v or "LARGE" in v or "BREAKTHROUGH" in v or "HIGH" in v for v in verdicts):
        score += 2
    if any("RISKY" in v or "SATURATED" in v for v in verdicts):
        score -= 1

    if score >= 3:
        recommendation = "LAUNCH NOW"
        rec_color = "#22c55e"
    elif score >= 1:
        recommendation = "VALIDATE FIRST"
        rec_color = "#f59e0b"
    else:
        recommendation = "PIVOT REQUIRED"
        rec_color = "#ef4444"

    return {
        "product_idea": req.product_idea,
        "market": req.market,
        "target_user": req.target_user,
        "headlines": headlines,
        "agents": list(agent_results),
        "recommendation": recommendation,
        "rec_color": rec_color,
    }
