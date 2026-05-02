import os, json, asyncio, re, httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
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

class BoardroomRequest(BaseModel):
    company: str
    ticker: str
    decision: str

# ─── Live Data Agents ────────────────────────────────────────────────
async def fetch_market_data(ticker: str) -> dict:
    """Fetch live stock data from Yahoo Finance (no API key needed)."""
    try:
        async with httpx.AsyncClient(timeout=10) as h:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
            r = await h.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = r.json()
            meta = data["chart"]["result"][0]["meta"]
            return {
                "price": round(meta.get("regularMarketPrice", 0), 2),
                "prev_close": round(meta.get("previousClose", 0), 2),
                "market_cap": meta.get("marketCap", "N/A"),
                "currency": meta.get("currency", "USD"),
                "exchange": meta.get("exchangeName", "N/A"),
            }
    except Exception as e:
        return {"price": "N/A", "prev_close": "N/A", "error": str(e)}

async def fetch_news_context(company: str) -> list[str]:
    """Scrape live Reuters RSS for company news headlines."""
    try:
        async with httpx.AsyncClient(timeout=8) as h:
            feed_url = f"https://feeds.reuters.com/reuters/businessNews"
            r = await h.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
            # Simple regex parse of RSS items
            titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", r.text)
            relevant = [t for t in titles if any(w in t.lower() for w in company.lower().split())]
            return relevant[:3] if relevant else titles[:3]
    except:
        return ["No live headlines available — using internal intelligence only."]

# ─── C-Suite Agent Factory ───────────────────────────────────────────
EXECUTIVES = [
    {
        "role": "CFO",
        "name": "Chief Financial Officer",
        "color": "#22c55e",
        "focus": "financial risk, ROI, cash flow, balance sheet impact, EPS dilution, debt covenants",
        "icon": "💰"
    },
    {
        "role": "COO",
        "name": "Chief Operating Officer",
        "color": "#3b82f6",
        "focus": "operational execution, supply chain, headcount, integration complexity, process risk",
        "icon": "⚙️"
    },
    {
        "role": "CTO",
        "name": "Chief Technology Officer",
        "color": "#a855f7",
        "focus": "technology stack compatibility, IP, data security, engineering capacity, technical debt",
        "icon": "💻"
    },
    {
        "role": "CMO",
        "name": "Chief Marketing Officer",
        "color": "#f97316",
        "focus": "brand impact, market positioning, customer sentiment, competitive response, TAM expansion",
        "icon": "📣"
    },
    {
        "role": "LEGAL",
        "name": "Chief Legal Officer",
        "color": "#ef4444",
        "focus": "regulatory compliance, antitrust risk, contract obligations, litigation exposure, IP liability",
        "icon": "⚖️"
    },
]

async def run_executive_agent(exec_info: dict, company: str, decision: str,
                               market_data: dict, news: list[str]) -> dict:
    """Run a single C-suite agent with live market context."""
    news_context = "\n".join(f"- {n}" for n in news)
    market_context = (
        f"Current Price: ${market_data.get('price', 'N/A')} | "
        f"Prev Close: ${market_data.get('prev_close', 'N/A')} | "
        f"Exchange: {market_data.get('exchange', 'N/A')}"
    )

    system_prompt = f"""You are the {exec_info['name']} ({exec_info['role']}) of a Fortune 500 company.
You are a hard-nosed executive with deep expertise in: {exec_info['focus']}.
Speak in the first person. Be direct, decisive, and specific. No fluff.
Keep your response under 120 words. End with a clear VERDICT: APPROVE / CONDITIONAL / REJECT."""

    user_prompt = f"""Company: {company}
Live Market Data: {market_context}
Breaking News Context:
{news_context}

PROPOSED DECISION: {decision}

As {exec_info['role']}, give your assessment. Include:
1. Your top 2 concerns specific to your domain
2. One opportunity you see
3. Your VERDICT"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=200
        )
        analysis = response.choices[0].message.content.strip()
        # Extract verdict
        verdict = "CONDITIONAL"
        if "APPROVE" in analysis.upper(): verdict = "APPROVE"
        elif "REJECT" in analysis.upper(): verdict = "REJECT"

        return {
            "role": exec_info["role"],
            "name": exec_info["name"],
            "color": exec_info["color"],
            "icon": exec_info["icon"],
            "analysis": analysis,
            "verdict": verdict
        }
    except Exception as e:
        return {
            "role": exec_info["role"],
            "name": exec_info["name"],
            "color": exec_info["color"],
            "icon": exec_info["icon"],
            "analysis": f"Agent offline: {str(e)}",
            "verdict": "CONDITIONAL"
        }

# ─── Routes ─────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f: return f.read()

@app.post("/boardroom")
async def boardroom(req: BoardroomRequest):
    print(f"🏛️ Convening Oracle Boardroom for: {req.company} | Decision: {req.decision}")

    # Fetch live data first, then run all 5 agents IN PARALLEL with real context
    market_data, news = await asyncio.gather(
        fetch_market_data(req.ticker),
        fetch_news_context(req.company),
    )

    agent_results = await asyncio.gather(
        *[run_executive_agent(exec_info, req.company, req.decision, market_data, news)
          for exec_info in EXECUTIVES]
    )

    # Board Tally
    verdicts = [a["verdict"] for a in agent_results]
    approve_count = verdicts.count("APPROVE")
    reject_count = verdicts.count("REJECT")
    conditional_count = verdicts.count("CONDITIONAL")

    if approve_count >= 3:
        board_decision = "APPROVED"
        board_color = "#22c55e"
    elif reject_count >= 3:
        board_decision = "REJECTED"
        board_color = "#ef4444"
    else:
        board_decision = "REVIEW REQUIRED"
        board_color = "#f97316"

    return {
        "company": req.company,
        "ticker": req.ticker,
        "decision": req.decision,
        "market_data": market_data,
        "news": news,
        "executives": list(agent_results),
        "board_decision": board_decision,
        "board_color": board_color,
        "tally": {
            "approve": approve_count,
            "conditional": conditional_count,
            "reject": reject_count
        }
    }
