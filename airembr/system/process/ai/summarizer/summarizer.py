import asyncio
from typing import Dict, Optional

from airembr.system.process.ai.summarizer.prompt import get_summary
from airembr.system.process.ai.summarizer.model.summary_output import SummaryOutput, SummaryPayload
from airembr.system.process.ai.memory.conversation.memory_facade import ConversationMemoryFacade
from airembr.model.system.context import Context, ServerContext, get_context
from airembr.model.api.response.conversation_memory import ConversationMemory


# This is expensive
async def get_summaries(conversation_memory: Dict[str, ConversationMemory], compression_sizes: Dict[str, int]) -> Dict[str, SummaryPayload]:
    summaries = {}
    for session_id, memory in conversation_memory.items():  # type: str, ConversationMemory

        max_length = int(compression_sizes.get(session_id, 102400))

        if memory.size() > max_length:
            try:
                memory_as_text = memory.to_text()

                # Add prev summary
                memory_as_text = f"Context:\n{memory.summary}\n\nConversation:\n{memory_as_text}"

                summary: Optional[SummaryOutput] = await get_summary(memory_as_text)

                if not summary:
                    continue

                summary = SummaryPayload(
                    summaries=summary.summaries,
                    topics=summary.topics,
                    ttl=memory.ttl,
                    no_of_passages=len(memory.passages)
                )
                summaries[session_id] = summary

            except Exception as e:
                print(e)
    return summaries


async def summary_job(context: Context, conversation_memory: Dict[str, ConversationMemory], ttls, compression_sizes: Dict[str, int]):
    with ServerContext(context):
        if conversation_memory:
            _summaries: Dict[str, SummaryPayload] = await get_summaries(conversation_memory, compression_sizes)

            if _summaries:
                for chat_id, summary_payload in _summaries.items():  # type: str, SummaryPayload
                    if summary_payload.summaries:
                        # Save summarized memory
                        memory = ConversationMemoryFacade(chat_id)
                        summarized_text = summary_payload.summaries_as_text()
                        memory.summary_memorize(summarized_text, expire=summary_payload.ttl if summary_payload.ttl>0 else ttls.get(chat_id, 86400))

                        # Delete chat history
                        new_passages = memory.chat_recall(summary_payload.no_of_passages)
                        if not new_passages:
                            memory.delete_chat()
                        else:
                            memory.chat_replace(*new_passages)

async def summary_worker(conversation_memory: Dict[str, ConversationMemory], ttls: Dict[str, int], compression_sizes: Dict[str, int]):
    asyncio.create_task(summary_job(get_context(), conversation_memory, ttls, compression_sizes))
