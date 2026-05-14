import os
import json
import re
import ast
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load .env from root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "meta/llama-3.1-8b-instruct"

class PulseRequest(BaseModel):
    brand_name: str
    strategic_query: str = ""
    recent_mentions: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

def send(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"

AGENTS = [
    {
        "key": "sentiment",
        "title": "Behavioral Data Scientist",
        "status": "Running Sentiment Analysis...",
        "system": (
            "You are an elite Behavioral Data Scientist. Analyze brand sentiment. "
            "After your analysis, output EXACTLY the following JSON and nothing else after it:\n"
            '{"score": <0-100>, "trajectory": "<Positive|Negative|Neutral>", '
            '"churn_risk": "<Low|Medium|High|Critical>", "key_drivers": ["<driver1>", "<driver2>", "<driver3>"]}'
        ),
    },
    {
        "key": "risk",
        "title": "Global Risk Strategist",
        "status": "Evaluating Risk Vectors...",
        "system": (
            "You are an elite Global Risk Strategist. Assess the brand's market risk. "
            "After your analysis, output EXACTLY the following JSON and nothing else after it:\n"
            '{"crisis_tier": "<1-5>", "strategic_pillars": ["<pillar1>", "<pillar2>", "<pillar3>"], '
            '"operational_requirements": ["<req1>", "<req2>", "<req3>"]}'
        ),
    },
    {
        "key": "content",
        "title": "Creative Communications Director",
        "status": "Designing Response Narrative...",
        "system": (
            "You are an elite Creative Communications Director. Design the brand response kit. "
            "After your analysis, output EXACTLY the following JSON and nothing else after it:\n"
            '{"tweet": "<max 20 words>", "press_headline": "<max 15 words>", '
            '"staff_action": "<max 15 words>"}'
        ),
    },
    {
        "key": "audit",
        "title": "Chief Orchestrator",
        "status": "Conducting Executive Audit...",
        "system": (
            "You are the Chief Orchestrator. Provide a final executive audit. "
            "After your analysis, output EXACTLY the following JSON and nothing else after it:\n"
            '{"verdict": "<10 words>", "summary": "<40 words, 2 sentences>", '
            '"actions": ["<action1 max 8 words>", "<action2 max 8 words>", "<action3 max 8 words>"], '
            '"refining_question": "<A follow-up question for the user to refine this analysis>"}'
        ),
    },
]

def extract_last_json(text: str) -> str:
    """Walk backwards from the last '}' to find the matching '{', handling nested braces."""
    end = text.rfind("}")
    if end == -1:
        return ""
    depth = 0
    for i in range(end, -1, -1):
        if text[i] == "}":
            depth += 1
        elif text[i] == "{":
            depth -= 1
            if depth == 0:
                return text[i:end + 1]
    return ""

async def stream_agent(agent: dict, brand_name: str, query: str, mentions: str):
    """Fetch full response, stream reasoning word-by-word, then emit final JSON."""
    import asyncio
    
    query_context = f"\n\nStrategic Goal/Question: {query}" if query else ""
    
    user_msg = (
        f"Brand: {brand_name}{query_context}\n\n"
        f"Live Feed:\n{mentions}\n\n"
        "Write a concise professional analysis (2-3 sentences). Then output the required JSON."
    )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": agent["system"]},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        stream=False,  # Full response — reliable JSON extraction
    )

    full_text = (response.choices[0].message.content or "").strip()

    # Extract the last valid JSON object from the response
    raw_json = extract_last_json(full_text)

    # Reasoning = everything before the JSON block
    if raw_json:
        json_pos = full_text.rfind(raw_json)
        reasoning = full_text[:json_pos].strip()
    else:
        reasoning = full_text

    # Strip any leftover tags or markdown artifacts from reasoning
    reasoning = re.sub(r"<[^>]+>", "", reasoning)
    reasoning = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", reasoning)
    reasoning = re.sub(r"\s+", " ", reasoning).strip()

    # Word-stream the reasoning for the live typing effect
    for word in reasoning.split():
        yield send({"agent": agent["key"], "thought_token": word + " "})
        await asyncio.sleep(0.025)

    # Parse and emit the JSON data
    if raw_json:
        data = None
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(raw_json)
            except Exception:
                pass
        if data and isinstance(data, dict):
            yield send({"agent": agent["key"], "final_data": data})
        else:
            yield send({"agent": agent["key"], "error": "Could not parse agent output."})
    else:
        yield send({"agent": agent["key"], "error": "No data object returned."})


async def swarm_generator(brand_name: str, query: str, mentions: str):
    for agent in AGENTS:
        yield send({"status": agent["status"]})
        async for chunk in stream_agent(agent, brand_name, query, mentions):
            yield chunk

    yield send({"status": "Mission Complete."})


@app.post("/analyze_stream")
async def analyze_stream(req: PulseRequest):
    return StreamingResponse(
        swarm_generator(req.brand_name, req.strategic_query, req.recent_mentions),
        media_type="text/event-stream",
    )
