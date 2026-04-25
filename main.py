from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from prompt import SYSTEM_PROMPT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PASSWORD = os.environ.get("BOT_PASSWORD", "123456")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

client = None

def get_client():
    global client
    if client is None:
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    return client

conversations: dict[str, list[dict]] = {}

class ChatRequest(BaseModel):
    message: str
    password: str
    session_id: str = "default"

class ResetRequest(BaseModel):
    password: str
    session_id: str = "default"

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.password != PASSWORD:
        raise HTTPException(status_code=403, detail="密码错误")

    if req.session_id not in conversations:
        conversations[req.session_id] = []

    conversations[req.session_id].append({"role": "user", "content": req.message})
    history = conversations[req.session_id][-20:]
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        api_messages.append({"role": m["role"], "content": m["content"]})

    async def event_stream():
        try:
            ds = get_client()
            stream = ds.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                max_tokens=1024,
                temperature=0.8,
                stream=True,
            )

            full = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full += text
                    yield f"data: {json.dumps({'t': text, 'd': False})}\n\n"

            conversations[req.session_id].append({"role": "assistant", "content": full})
            yield f"data: {json.dumps({'t': '', 'd': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'t': f'出错: {str(e)}', 'd': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/reset")
def reset(req: ResetRequest):
    if req.password != PASSWORD:
        raise HTTPException(status_code=403, detail="密码错误")
    conversations[req.session_id] = []
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
