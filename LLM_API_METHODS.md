# LLM API Integration - HTTP Request Method

## Overview
This project now uses **direct HTTP requests** for LLM integration instead of the OpenAI Python SDK. This provides better compatibility with proxy sites and alternative providers.

## Configuration

### Environment Variables (.env)

```bash
# Base URL for the LLM API (without the endpoint path)
LLM_BASE_URL=https://api.oaipro.com

# API Key for authentication
LLM_API_KEY=your_api_key_here

# Model name to use
LLM_MODEL=gpt-4o-mini
```

### Example Configurations

**For api.oaipro.com:**
```bash
LLM_BASE_URL=https://api.oaipro.com
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini
```

**For OpenAI:**
```bash
LLM_BASE_URL=https://api.openai.com
LLM_API_KEY=sk-your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
```

## API Endpoint

The client uses the **Chat Completions API** format:
- **Endpoint:** `{LLM_BASE_URL}/v1/chat/completions`
- **Method:** POST
- **Content-Type:** application/json
- **Authorization:** Bearer {LLM_API_KEY}

## Request Format

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "{instructions}\n\n---\n\nInput Data:\n{input}"
    }
  ],
  "temperature": 0.1,
  "max_tokens": 10000
}
```

## Response Format

The client expects responses in OpenAI-compatible format:

```json
{
  "choices": [
    {
      "message": {
        "content": "Generated text response"
      }
    }
  ]
}
```

## Code Example

```python
from src.open_dictionary.llm.llm_client import get_chat_response

# Get LLM response
response = get_chat_response(
    instructions="You are a helpful assistant.",
    input="Translate this text to Chinese."
)

print(response)
```

## Testing

Run the MVP test to verify the setup:

```bash
python test_mvp.py
```

This will:
1. Process mock Japanese dictionary entries
2. Generate Chinese definitions using the LLM
3. Save results to JSON and JSONL files

## Benefits

✅ **No SDK Dependencies** - Uses standard `requests` library
✅ **Provider Agnostic** - Works with any OpenAI-compatible API
✅ **Proxy Site Friendly** - Perfect for sites like api.oaipro.com
✅ **Connection Pooling** - Reuses HTTP sessions for efficiency
✅ **Error Handling** - Comprehensive error messages with status codes

## Troubleshooting

**Authentication Error (401):**
- Check your `LLM_API_KEY` is correct
- Verify the key has proper permissions

**Connection Error:**
- Verify `LLM_BASE_URL` is accessible
- Check your internet connection
- Ensure the endpoint path is correct

**Timeout Error:**
- The client has a 60-second timeout
- For large requests, consider reducing max_tokens
