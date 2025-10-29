import json
import requests
from typing import Dict, Any
from open_dictionary.utils.env_loader import get_env

# Global session for connection pooling
_session = None

def _get_session() -> requests.Session:
    """Get or create a requests session with connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session

def get_chat_response(instructions: str, input: str) -> str:
    """
    Get a chat response from the LLM using HTTP requests.

    Args:
        instructions: System instructions for the LLM
        input: User input/data

    Returns:
        The LLM's response text
    """
    # Get configuration from environment
    base_url = get_env('LLM_BASE_URL')
    api_key = get_env('LLM_API_KEY')
    model = get_env('LLM_MODEL')

    if not base_url:
        raise RuntimeError(
            "LLM_BASE_URL is not set in environment variables.\n"
            "Please check your .env file."
        )

    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY is not set in environment variables.\n"
            "Please check your .env file."
        )

    # Construct the endpoint URL
    # Most providers use /v1/chat/completions endpoint
    endpoint = f"{base_url.rstrip('/')}/v1/chat/completions"

    # Prepare the messages
    # Combine instructions and input into a single user message
    full_input = f"{instructions}\n\n---\n\nInput Data:\n{input}"

    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "user", "content": full_input}
        ],
        "temperature": 0.1,
        "max_tokens": 10000
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    session = _get_session()

    try:
        response = session.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response
        result = response.json()

        # Extract the response text from the choices
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise RuntimeError(f"Unexpected response format: {result}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Failed to get LLM response: {e}\n"
            f"Endpoint: {endpoint}\n"
            f"Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}\n"
            f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}"
        ) from e
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Failed to parse LLM response: {e}\n"
            f"Response content: {response.text if 'response' in locals() else 'N/A'}"
        ) from e
