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

    # Determine which API method to use (default to 'responses')
    api_method = get_env('LLM_METHOD', default='responses').lower()

    # Map method names to client attributes
    # 'chat' maps to 'chat.completions', others use themselves
    method_map = {
        'responses': 'responses',
        'chat': 'chat.completions'
    }

    if api_method not in method_map:
        raise ValueError(
            f"Invalid LLM_METHOD: {api_method}. "
            "Must be either 'responses' or 'chat'."
        )

    client_attr = method_map[api_method]

    # Use dynamic attribute access: client.{}.create()
    api_endpoint = getattr(client, client_attr)

    # Prepare parameters based on API method
    if api_method == 'responses':
        response = api_endpoint.create(
            model=get_env('LLM_MODEL'),
            instructions=instructions,
            input=input,
            temperature=0.1
        )
        return response.output_text
    else:  # chat
        # Combine instructions and input into a single message
        full_input = f"{instructions}\n\n---\n\nInput Data:\n{input}"

        response = api_endpoint.create(
            model=get_env('LLM_MODEL'),
            messages=[
                {"role": "user", "content": full_input}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
