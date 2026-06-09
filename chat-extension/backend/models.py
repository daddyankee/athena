from pydantic import BaseModel
from typing import Optional


class Config(BaseModel):
    mock: bool = True
    humanize: bool = False
    developer: bool = False


class ChatRequest(BaseModel):
    messages: list[dict]
    config: Config = Config()
    conversation_id: Optional[str] = None
