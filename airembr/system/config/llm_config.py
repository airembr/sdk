import os

from airembr.core.singleton import Singleton


class LlmConfig(metaclass=Singleton):
    def __init__(self):
        env = os.environ
        self.llm_token = env.get('LLM_TOKEN', None)
        self.llm_provider = env.get('LLM_PROVIDER', 'openrouter')
        self.llm_model = env.get('LLM_MODEL', 'google/gemini-2.5-flash-lite')  # openai/gpt-5-nano

llm_config = LlmConfig()