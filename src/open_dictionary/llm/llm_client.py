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
    # 'chat' uses client.chat.completions, 'responses' uses client.responses
    method_map = {
        'responses': ('responses', None),
        'chat': ('chat', 'completions')
    }

    if api_method not in method_map:
        raise ValueError(
            f"Invalid LLM_METHOD: {api_method}. "
            "Must be either 'responses' or 'chat'."
        )

    attr_name, sub_attr = method_map[api_method]

    # Use dynamic attribute access with nested attributes if needed
    if sub_attr:
        # For 'chat.completions': getattr(getattr(client, 'chat'), 'completions')
        api_endpoint = getattr(getattr(client, attr_name), sub_attr)
    else:
        # For 'responses': getattr(client, 'responses')
        api_endpoint = getattr(client, attr_name)

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
