import os

embedding_host = os.environ.get("EMBEDDING_HOST", None)
embedding_api_key = os.environ.get("EMBEDDING_API_KEY", None)

LLM_ENTITY_EXTRACTION_MODEL = 'minimax/minimax-m2.5'
# LLM_ENTITY_EXTRACTION_MODEL = 'minimax/minimax-m2.7'
LLM_ENTITY_EXTRACTION_MODEL = 'openai/gpt-5.2'
LLM_ENTITY_EXTRACTION_MODEL = 'google/gemma-4-26b-a4b-it'
LLM_ENTITY_EXTRACTION_MODEL = 'deepseek/deepseek-chat-v3-0324'

LLM_ENTITY_EXTRACTION_MODEL = 'openai/gpt-5.4-nano'
LLM_ENTITY_EXTRACTION_MODEL = 'minimax/minimax-m2.5'
LLM_ENTITY_EXTRACTION_MODEL = 'mistralai/ministral-3b-2512'

LLM_ENTITY_EXTRACTION_MODEL = 'qwen/qwen3-max-thinking'
LLM_ENTITY_EXTRACTION_MODEL = 'mistralai/mistral-small-3.2-24b-instruct'
LLM_ENTITY_EXTRACTION_MODEL = 'google/gemma-4-26b-a4b-it'
LLM_ENTITY_EXTRACTION_MODEL = 'mistralai/ministral-14b-2512'

SECOND_LLM_ENTITY_EXTRACTION_MODEL = 'mistralai/mistral-small-3.2-24b-instruct'
SECOND_LLM_ENTITY_EXTRACTION_MODEL = 'google/gemma-4-26b-a4b-it'
SECOND_LLM_ENTITY_EXTRACTION_MODEL = 'mistralai/ministral-14b-2512'

LLM_QUERY_MODEL = 'qwen/qwen3-max-thinking'
LLM_QUERY_MODEL = 'google/gemma-4-26b-a4b-it' # better

LLM_PROVIDER = 'open-router'
LLM_PROVIDER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
