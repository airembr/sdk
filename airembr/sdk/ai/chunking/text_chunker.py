from typing import Callable

import semchunk

try:
    import tiktoken
    _tokenizer = tiktoken.get_encoding('cl100k_base')
except ImportError:
    _tokenizer = None


def get_text_chunker(chunk_size: int) -> Callable[[str], list[str]]:
    if _tokenizer is not None:
        return semchunk.chunkerify(_tokenizer, chunk_size)
    return semchunk.chunkerify(lambda text: len(text.split()), chunk_size)
