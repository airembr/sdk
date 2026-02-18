
class LLMAdapterError(Exception):
    """Base adapter exception."""


class ProviderNotSupportedError(LLMAdapterError):
    """Raised when unsupported provider is used."""
