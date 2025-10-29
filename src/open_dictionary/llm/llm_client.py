from openai import OpenAI
from open_dictionary.utils.env_loader import get_env

# Lazy initialization - client will be created when first used
_client = None

def _get_client():
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        try:
            _client = OpenAI(
                api_key=get_env('LLM_KEY'),
                base_url=get_env('LLM_API'),
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize LLM client: {e}\n"
                "Please check your LLM_KEY and LLM_API environment variables in .env"
            ) from e
    return _client

def get_chat_response(instructions: str, input: str) -> str:
    """
    Get a chat response from the LLM.
    
    Args:
        instructions: System instructions for the LLM
        input: User input/data
        
    Returns:
        The LLM's response text
    """
    client = _get_client()
    
    response = client.responses.create(
        model=get_env('LLM_MODEL'),
        instructions=instructions,
        input=input,
        temperature=0.1
    )
    
    return response.output_text
