from airembr.system.adapter.cache.cache_adaper_selector import list_cache_adapter


class ConversationMemoryFacade:

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self._summary_adapter = list_cache_adapter(f"summary")
        self._chat_adapter = list_cache_adapter(f"chat")
        self._context_adapter = list_cache_adapter(f"context")

    def chat_memorize(self, *values: str):
        return self._chat_adapter.rpush(self.conversation_id, *values)

    def chat_replace(self, value: str):
        self._chat_adapter.delete(self.conversation_id)
        return self._chat_adapter.rpush(self.conversation_id, value)

    def chat_recall(self, start: int = 0, end: int = -1):
        return [item.decode() for item in self._chat_adapter.lrange(self.conversation_id, start, end)]

    def chat_forget(self, ttl):
        return self._chat_adapter.expire(self.conversation_id, ttl)

    def chat_ttl(self):
        return self._chat_adapter.ttl(self.conversation_id)

    def delete_chat(self):
        self._chat_adapter.delete(self.conversation_id)

    # Context

    def context_memorize(self, entity, value, expire=None):
        return self._context_adapter.set(f"{self.conversation_id}:{entity}", value, ex=expire)

    def context_recall(self, entity):
        return self._context_adapter.get(f"{self.conversation_id}:{entity}")

    def context_ttl(self, entity):
        return self._context_adapter.ttl(f"{self.conversation_id}:{entity}")

    def context_forget(self, entity, ttl):
        return self._context_adapter.expire(f"{self.conversation_id}:{entity}", ttl)

    def summary_memorize(self, value, expire=None):
        return self._summary_adapter.set(self.conversation_id, value, ex=expire)

    def summary_recall(self):
        return self._summary_adapter.get(self.conversation_id)

    def summary_ttl(self):
        return self._summary_adapter.ttl(self.conversation_id)

    def summary_forget(self, ttl):
        return self._summary_adapter.expire(self.conversation_id, ttl)
