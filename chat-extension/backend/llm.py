import asyncio
import os
from openai import AsyncOpenAI

MOCK_RESPONSE = """Hey — Athena here. Running in mock mode so no API calls are going out.

Each word streams in one at a time, same cadence as a real model. You can see the cursor blink, auto-scroll, and multi-turn memory staying intact.

Try toggling Humanize or Developer above — in real mode those flip the system prompt sent to the model. Both can be active at once.

When you're ready: turn Mock off, drop your DEEPSEEK_API_KEY in .env, and it goes live."""


async def mock_stream():
    words = MOCK_RESPONSE.split(" ")
    for i, word in enumerate(words):
        yield word if i == 0 else " " + word
        await asyncio.sleep(0.04)


async def deepseek_stream(messages: list[dict]):
    client = AsyncOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    stream = await client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
