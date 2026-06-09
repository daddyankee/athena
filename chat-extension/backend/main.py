from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import json

from models import ChatRequest
from prompts import build_messages
from db import init, create_conversation, touch_conversation, save_message, list_conversations, get_messages
from llm import mock_stream, deepseek_stream

load_dotenv()
init()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(req: ChatRequest):
    user_msg = req.messages[-1]["content"] if req.messages else ""

    cid = req.conversation_id
    if not cid:
        cid = create_conversation(user_msg[:80].strip())

    save_message(cid, "user", user_msg)

    source = mock_stream() if req.config.mock else deepseek_stream(build_messages(req.messages, req.config))

    async def generate():
        chunks = []
        async for token in source:
            chunks.append(token)
            yield f"data: {json.dumps({'content': token})}\n\n"

        save_message(cid, "assistant", "".join(chunks))
        touch_conversation(cid)

        yield f"data: {json.dumps({'meta': {'conversation_id': cid}})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/conversations")
async def conversations(limit: int = 15, offset: int = 0):
    return list_conversations(limit, offset)


@app.get("/conversations/{cid}/messages")
async def messages(cid: str):
    return get_messages(cid)
