import os, json, asyncio, re, httpx
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

# ─── Request Model ────────────────────────────────────────────────────
class NexusRequest(BaseModel):
    linkedin_url: str    # e.g. https://linkedin.com/in/umang-yadav
    your_product: str    # e.g. AI Agent Platform
    your_company: str    # e.g. NovaTech AI
    value_prop: str      # e.g. 10x faster agent deployment

# ─── LinkedIn Public Profile Scraper ─────────────────────────────────
async def scrape_linkedin(url: str) -> dict:
    """Fetch public LinkedIn profile metadata from og: tags."""
    profile = {"name": "", "headline": "", "company": "", "url": url, "username": ""}

async def scrape_linkedin(url: str) -> dict:
    """Fetch public LinkedIn profile metadata from og: tags."""
    profile = {"name": "", "headline": "", "company": "", "url": url, "username": "", "description": ""}

    # Extract username from URL
    match = re.search(r'linkedin\.com/in/([^/?]+)', url)
    if match:
        username_slug = match.group(1)
        profile["username"] = username_slug
        # Convert "umang-yadav" to "Umang Yadav"
        profile["name"] = username_slug.replace("-", " ").replace(".", " ").title()

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=5, follow_redirects=True) as h:
            r = await h.get(url, headers=headers)
            if r.status_code == 200:
                html = r.text
                og_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                og_desc  = re.search(r'<meta property="og:description" content="([^"]+)"', html)

                if og_title:
                    title_text = og_title.group(1)
                    parts = title_text.replace(" | LinkedIn", "").split(" - ", 1)
                    if parts: profile["name"] = parts[0].strip()
                    if len(parts) > 1: profile["headline"] = parts[1].strip()

                if og_desc:
                    profile["description"] = og_desc.group(1)[:500]
    except Exception as e:
        print(f"Scrape attempt failed: {e}")

    return profile

async def enrich_profile(profile: dict) -> dict:
    """If scrape was blocked, use AI to infer professional context from the username/slug."""
    if profile.get("headline") and len(profile["headline"]) > 5:
        return profile # Already have data

    prompt = f"Given the LinkedIn username '{profile['username']}', infer a likely professional profile (Role, Industry, Interests). Be realistic. Return only JSON: {{\"name\": \"...\", \"headline\": \"...\", \"description\": \"...\"}}"
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are a LinkedIn Data Enrichment agent."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        enriched = json.loads(response.choices[0].message.content)
        profile.update(enriched)
    except: pass
    return profile

# ─── Agent Configs ────────────────────────────────────────────────────
AGENTS = [
    {
        "role": "PROFILER",
        "name": "Prospect Intelligence Analyst",
        "icon": "🔍",
        "color": "#06b6d4",
    },
    {
        "role": "PITCH",
        "name": "LinkedIn InMail Architect",
        "icon": "✍️",
        "color": "#a855f7",
    },
    {
        "role": "OBJECTIONS",
        "name": "Objection Handler",
        "icon": "🛡️",
        "color": "#f97316",
    },
    {
        "role": "FOLLOWUP",
        "name": "Follow-Up Sequence Writer",
        "icon": "📅",
        "color": "#22c55e",
    },
]

AGENT_PROMPTS = {
    "PROFILER": """You are a B2B Sales Intelligence expert.
Based on the prospect's LinkedIn profile, infer:
1. Their likely #1 business pain point
2. Their buying personality (Analytical/Visionary/Driver/Amiable)
3. Best time/channel to approach them
Be specific and insightful. Under 100 words.
End with: PERSONALITY: [type] | FIT SCORE: [0-100]/100""",

    "PITCH": """You are a LinkedIn InMail copywriter who closes 7-figure deals.
Write a personalized LinkedIn InMail (connection request note) for this prospect.
Rules: Under 300 characters (LinkedIn limit). Reference something specific about them.
Make the first line impossible to ignore. End with a soft CTA, not a hard sell.
Then write a longer follow-up InMail message (under 150 words) for after they accept.
End with: SEND CONFIDENCE: HIGH/MEDIUM/LOW""",

    "OBJECTIONS": """You are a sales objection expert.
List the 3 most likely objections this prospect will raise and your killer response to each.
Be specific to their role, company, and industry.
Format: Objection → Response. Under 120 words total.
End with: RISK LEVEL: HIGH/MEDIUM/LOW""",

    "FOLLOWUP": """You are a B2B sales sequence strategist.
Design a 3-touch follow-up sequence if they don't respond to the first InMail:
- Touch 2 (Day 3): Short value-add message
- Touch 3 (Day 7): Break-up message with a hook
Keep each under 50 words. Make them human, not automated.
End with: SEQUENCE TYPE: AGGRESSIVE/BALANCED/NURTURE""",
}

async def run_agent(agent: dict, profile: dict, req: NexusRequest) -> dict:
    profile_ctx = f"""PROSPECT:
Name: {profile.get('name', 'Unknown')}
LinkedIn Headline: {profile.get('headline', 'N/A')}
LinkedIn URL: {profile.get('url')}
Profile Description: {profile.get('description', 'N/A')}

YOUR OFFER:
Product: {req.your_product}
Company: {req.your_company}
Value Proposition: {req.value_prop}"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": AGENT_PROMPTS[agent["role"]]},
                {"role": "user", "content": profile_ctx},
            ],
            temperature=0.5,
            max_tokens=280,
        )
        analysis = response.choices[0].message.content.strip()
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

@app.post("/nexus")
async def nexus(req: NexusRequest):
    print(f"📡 Nexus scanning: {req.linkedin_url}")

    # Step 1: Scrape LinkedIn profile
    profile = await scrape_linkedin(req.linkedin_url)
    
    # Step 2: Enrich profile if scrape was blocked
    profile = await enrich_profile(profile)
    print(f"✅ Profile ready: {profile.get('name', 'Unknown')}")

    # Step 3: Run all 4 agents in parallel
    agent_results = await asyncio.gather(
        *[run_agent(a, profile, req) for a in AGENTS]
    )

    return {
        "profile": profile,
        "your_product": req.your_product,
        "your_company": req.your_company,
        "agents": list(agent_results),
    }
