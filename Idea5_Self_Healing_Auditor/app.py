import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File
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

# Use the faster 8b model for rapid code auditing
MODEL = "meta/llama-3.1-8b-instruct"

class AuditRequest(BaseModel):
    code: str

async def call_agent(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    try:
        kwargs = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2, # Lower temperature for precision coding
            "max_tokens": 4096
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

@app.post("/audit")
async def audit_code(req: AuditRequest):
    print(f"🕵️‍♂️ Initializing Code Audit...")
    
    auditor_sys = """You are a Senior Security Auditor and Code Architect.
    Analyze the provided Python code for security vulnerabilities, logic bugs, and performance bottlenecks.
    Identify 3-5 specific issues.
    For each issue, provide a description and the exact fix.
    
    Return ONLY a JSON object:
    {
      "summary": "High-level audit summary",
      "issues": [
        {
          "type": "Security|Logic|Performance",
          "severity": "Critical|High|Medium",
          "desc": "Explanation of the issue",
          "original": "The specific line or block causing the issue",
          "fixed": "The exact fixed replacement code"
        }
      ],
      "healed_code": "The full, complete file content with all identified fixes applied"
    }"""

    res_raw = await call_agent(auditor_sys, f"Code to Audit:\n\n{req.code}", json_mode=True)
    
    try:
        data = json.loads(res_raw)
        return data
    except Exception as e:
        print(f"❌ Audit Failure: {e}")
        return {"error": "Failed to parse audit results.", "raw": res_raw}
