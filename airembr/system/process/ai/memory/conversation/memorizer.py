from contextlib import asynccontextmanager
from typing import Tuple, List, Dict, Optional

from airembr.system.decorator.run_every import run_every
from airembr.model.api.response.conversation_memory import ConversationMemory
from airembr.system.process.ai.memory.conversation.memory_facade import ConversationMemoryFacade
from airembr.system.process.ai.memory.conversation.summarizer import summary_worker


def get_conversation_memory(chat_id: str) -> Tuple[List[str], int]:
    memory = ConversationMemoryFacade(chat_id)
    return memory.chat_recall(), memory.chat_ttl()


def _yield_conversation_memories(chat_ids):
    for chat_id in chat_ids:
        memory, ttl = get_conversation_memory(chat_id)
        yield chat_id, memory, ttl if ttl > 0 else 0


async def load_conversation_memories(collector) -> Optional[Dict[str, ConversationMemory]]:
    mems = {}
    chat_ids = collector.get_chat_ids()

    if not chat_ids:
        return None

    # Memory
    for session_id, memories, ttl in _yield_conversation_memories(chat_ids):

        mem = ConversationMemory(
            id=session_id,
            passages=memories,
            ttl=ttl if ttl > 0 else collector.get_ttl(session_id, 2629746)
        )

        mems[session_id] = mem

    return mems


def load_summary(chat_id):
    memory = ConversationMemoryFacade(chat_id)
    return memory.summary_recall()


async def load_memories_context(collector) -> Optional[Dict[str, ConversationMemory]]:
    mems = await load_conversation_memories(collector)

    if mems is None:
        return {}

    # Add summaries
    for chat_id, mem in mems.items():
        summary = load_summary(chat_id)
        if summary:
            mem.summary = load_summary(chat_id).decode()

    # Add participants
    for chat_id, participants in collector.get_participants().items():
        if chat_id in mems:
            m = mems[chat_id]
            m.entities = participants

    # Current

    for session_id, is_chat, chat_ttl, should_chat_ttl_be_overridden, texts in collector.get_semantic_text():
        if is_chat:
            historical_memory = mems.get(session_id, None)
            if historical_memory is not None:
                if should_chat_ttl_be_overridden:
                    historical_memory.ttl = collector.get_ttl(session_id, 2629746)
                    historical_memory.passages = texts
                else:
                    historical_memory.passages.extend(texts)

    return mems if mems else None


def _get_semantic_text(observations):
    for observation in observations:
        texts = []
        for rel in observation.relation:
            if rel.has_sematic_part() and rel.text.summaries:
                texts.append(f"{rel.actor.role if rel.actor.role else '_'}:{rel.text.summaries}")
        yield observation.get_session_id(), observation.is_chat(), observation.get_chat_ttl(), observation.should_chat_ttl_be_overridden(), texts


@run_every(interval=10)
def _slow_forget_update(stm, chat_ttl):
    stm.chat_forget(chat_ttl)


def save_conversation_memory(ttls: Dict[str, int], semantic_texts):
    for chat_id, is_chat, chat_ttl, should_chat_ttl_be_overridden, texts in semantic_texts:
        if is_chat and texts:
            stm = ConversationMemoryFacade(chat_id)

            no_of_chats = stm.chat_memorize(*texts)
            if chat_ttl > 0:
                if no_of_chats < 3:
                    stm.chat_forget(chat_ttl)
                else:
                    _slow_forget_update(stm, chat_ttl)
            else:
                chat_ttl = ttls.get(chat_id, 2629746) # Month
                stm.chat_forget(chat_ttl)


@asynccontextmanager
async def memorizer(collector):
    conversation_memory = await load_memories_context(collector)

    yield conversation_memory

    ttls = collector.get_ttls()
    compression_sizes = collector.get_compression_sizes()

    # Save new memories (it is quick)
    save_conversation_memory(ttls, collector.get_semantic_text())

    # Schedule: Summarize conversation when max size is reached
    if conversation_memory:
        await summary_worker(conversation_memory, ttls, compression_sizes)
