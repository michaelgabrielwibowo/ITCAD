from .mock_adapter import MockLLMAdapter
from .command_adapter import CommandModelAdapter

def get_adapter(adapter_name: str):
    if adapter_name == "mock":
        return MockLLMAdapter()
    elif adapter_name == "command":
        return CommandModelAdapter()
    elif adapter_name == "openai":
        from .openai_adapter import OpenAIAdapter
        return OpenAIAdapter()
    elif adapter_name == "gemini":
        from .gemini_adapter import GeminiAdapter
        return GeminiAdapter()
    elif adapter_name == "ollama":
        from .ollama_adapter import OllamaAdapter
        return OllamaAdapter()

    raise ValueError(f"Adapter '{adapter_name}' not recognized or configured.")
