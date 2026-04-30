import os
import json
import asyncio
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

class GraphRequest(BaseModel):
    topic: str

async def call_agent(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    try:
        kwargs = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 2000
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.post("/generate_graph")
async def generate_graph(req: GraphRequest):
    print(f"🚀 Launching Deep Intelligence Swarm for: {req.topic}")
    
    engine_sys = """You are a Deep Knowledge Architect. Map out the provided topic into a structured graph.
    Identify 5 main pillars and 2-3 sub-concepts for each. 
    For EVERY node (pillar and sub-concept), provide a 2-sentence expert description.
    Identify 3-4 cross-links between pillars.
    Return ONLY a JSON object:
    {
      "pillars": [
        {
          "name": "Pillar Name",
          "description": "Expert 2-sentence description.",
          "subs": [
            {"name": "Sub Name", "description": "Expert description."}
          ],
          "links_to": ["Other Pillar Name"]
        }
      ]
    }"""

    res_raw = await call_agent(engine_sys, f"Topic: {req.topic}", json_mode=True)
    
    try:
        data = json.loads(res_raw)
        nodes = [{"id": req.topic, "name": req.topic, "desc": f"Root node for {req.topic}", "val": 25, "color": "#10b981", "group": 0}]
        links = []
        
        for p in data.get("pillars", []):
            p_name = p["name"]
            nodes.append({"id": p_name, "name": p_name, "desc": p.get("description", ""), "val": 18, "color": "#3b82f6", "group": 1})
            links.append({"source": req.topic, "target": p_name, "color": "#3b82f6"})
            
            for sub_obj in p.get("subs", []):
                sub_name = sub_obj["name"]
                nodes.append({"id": sub_name, "name": sub_name, "desc": sub_obj.get("description", ""), "val": 10, "color": "#8b5cf6", "group": 2})
                links.append({"source": p_name, "target": sub_name, "color": "#8b5cf6"})
                
            for target in p.get("links_to", []):
                links.append({"source": p_name, "target": target, "color": "rgba(255,255,255,0.2)", "curvature": 0.2})
                
        return {"nodes": nodes, "links": links}
    except Exception as e:
        print(f"❌ Swarm Error: {e}")
        return {"nodes": [], "links": []}
