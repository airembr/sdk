import semchunk
import tiktoken  # `transformers` and `tiktoken` are not required.
from transformers import AutoTokenizer  # They're just here for demonstration purposes.


def get_text_semantic_chunker(chunk_size):
    # does not know how many special tokens, if any, your tokenizer adds to every input,
    # so you may want to deduct the number of special tokens added from your chunk size.

    # You can construct a chunker with `semchunk.chunkerify()` by passing the name of an OpenAI model,
    # OpenAI `tiktoken` encoding or Hugging Face model, or a custom tokenizer that has an `encode()`
    # method (like a `tiktoken`, `transformers` or `tokenizers` tokenizer) or a custom token counting
    # function that takes a text and returns the number of tokens in it.
    return semchunk.chunkerify('isaacus/kanon-tokenizer', chunk_size) or \
        semchunk.chunkerify('gpt-4', chunk_size) or \
        semchunk.chunkerify('cl100k_base', chunk_size) or \
        semchunk.chunkerify(AutoTokenizer.from_pretrained('isaacus/kanon-tokenizer'), chunk_size) or \
        semchunk.chunkerify(tiktoken.encoding_for_model('gpt-4'), chunk_size) or \
        semchunk.chunkerify(lambda text: len(text.split()), chunk_size)
