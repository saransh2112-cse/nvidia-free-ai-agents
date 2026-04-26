import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

app = FastAPI()

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

# Models
MODEL_LLAMA = "meta/llama-3.1-70b-instruct"
MODEL_MIXTRAL = "mistralai/mixtral-8x22b-instruct-v0.1"

system_llama = "You are Llama 3. You are participating in a debate. You firmly believe that critical thinking is the most important skill. Defend your position logically and concisely (max 1 paragraph per response). Keep it brief."
system_mixtral = "You are Mixtral. You are participating in a debate. You firmly believe that adaptability and continuous learning are the most important skills. Defend your position logically and concisely (max 1 paragraph per response). Keep it brief."

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return f.read()

@app.get("/stream-debate")
async def stream_debate(topic: str = "What is the most important skill for a software engineer in the age of AI?", turns: int = 2):
    async def event_generator():
        yield f"data: {json.dumps({'type': 'system', 'content': f'Starting debate on topic: {topic}'})}\n\n"
        
        history_llama = [{"role": "system", "content": system_llama}]
        history_mixtral = [{"role": "system", "content": system_mixtral}]
        
        current_speaker = "Llama"
        current_model = MODEL_LLAMA
        last_message = f"Let's debate the following topic: {topic}"
        
        # Initial prompt to Llama
        history_llama.append({"role": "user", "content": last_message})
        
        for turn in range(turns * 2):
            yield f"data: {json.dumps({'type': 'speaker', 'name': current_speaker, 'model': current_model})}\n\n"
            
            history = history_llama if current_speaker == "Llama" else history_mixtral
            model = MODEL_LLAMA if current_speaker == "Llama" else MODEL_MIXTRAL
            
            # Streaming response
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=history,
                    stream=True,
                    temperature=0.7,
                    max_tokens=250
                )
                
                full_reply = ""
                async for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_reply += content
                        # Escape newlines for SSE
                        clean_content = content.replace('\n', '\\n')
                        yield f"data: {json.dumps({'type': 'token', 'content': clean_content})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                # Append assistant reply to its own history
                history.append({"role": "assistant", "content": full_reply})
                
                # Switch speaker and pass the reply as user message
                if current_speaker == "Llama":
                    current_speaker = "Mixtral"
                    current_model = MODEL_MIXTRAL
                    history_mixtral.append({"role": "user", "content": f"Llama argues: {full_reply}\n\nWhat is your counter-argument?"})
                else:
                    current_speaker = "Llama"
                    current_model = MODEL_LLAMA
                    history_llama.append({"role": "user", "content": f"Mixtral argues: {full_reply}\n\nWhat is your counter-argument?"})
                    
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                break
                
            await asyncio.sleep(1) # Small pause between turns
            
        yield f"data: {json.dumps({'type': 'system', 'content': 'Debate concluded.'})}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
