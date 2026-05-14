from typing import List, Optional, Dict

from pydantic import BaseModel
from datetime import datetime


class TimeModel(BaseModel):
    datetime: datetime
    day: str

    def __str__(self):
        return f"{self.datetime} ({self.day})"


class ConversationMemory(BaseModel):
    id: str
    time: TimeModel = TimeModel(datetime=datetime.utcnow(), day=datetime.utcnow().strftime("%A"))
    passages: List[str] = []
    topics: List[str] = []
    entities: List[str] = []
    ner: List[str] = []
    summary: Optional[str] = None
    ttl: int

    def to_text(self):
        return "\n".join(self.passages)

    def size(self):
        return len(self.to_text())

    def get_context_as_json(self):
        return self.model_dump_json(exclude={"id": ..., "time": ..., "ttl": ...})

    def format(self):
        return format_conversation_memory(self)


class MemorySessions(dict):

    def get_chat_memory(self, chat_id) -> Optional[ConversationMemory]:
        return self.get(chat_id, None)


def _join(list, default="\n"):
    return default.join(list)


def format_conversation_memory(memory: ConversationMemory):
    text = ""
    if memory.summary:
        text += f"Summary of previous chat:\n{memory.summary}"

    if memory.topics:
        text += f"\n\nTopics of conversation:\n{_join(memory.topics, ', ')}"

    if memory.entities or memory.ner:
        text += f"\n\nEntities of conversation:\n"
        if memory.entities:
            text += f"{_join(memory.entities)}\n"
        if memory.ner:
            text += _join(memory.ner)

    text += f"\n\nCurrent prompt:\n{_join(memory.passages)}"

    if memory.time:
        text += f"\n\nNow:\n{memory.time.datetime} ({memory.time.day})\n"
    return text


def format_conversation_memories(conversation_memory: Dict[str, ConversationMemory]):
    result = {}

    for chat_id, memory in conversation_memory.items():
        text = format_conversation_memory(memory)

        result[chat_id] = text

    return result
