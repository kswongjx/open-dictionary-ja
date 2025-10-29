# LLM API Methods Configuration Guide

## Overview
The LLM client now supports both OpenAI's `Responses API` and `Chat Completions API`. You can choose which one to use via the `LLM_METHOD` environment variable.

## Configuration

### Using Responses API (Recommended)
This is the newer, more advanced API from OpenAI.

**.env configuration:**
```bash
LLM_METHOD=responses
LLM_API=https://api.openai.com/v1
LLM_KEY=sk-your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
```

**How it works:**
- Uses `client.responses.create()`
- Supports `instructions` parameter for system prompts
- Better structured output handling
- More accurate JSON responses

**Best for:**
- Complex tasks requiring structured output
- JSON generation (like dictionary definitions)
- Multi-step reasoning

### Using Chat Completions API
This is the traditional chat-based API.

**.env configuration:**
```bash
LLM_METHOD=chat
LLM_API=https://api.openai.com/v1
LLM_KEY=sk-your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
```

**How it works:**
- Uses `client.chat.completions.create()`
- Combines instructions and input into a single user message
- Returns `response.choices[0].message.content`
- Simpler but less structured

**Best for:**
- General conversation
- Simple text generation
- Backwards compatibility

## Code Implementation

The `get_chat_response()` function automatically detects the API method:

```python
def get_chat_response(instructions: str, input: str) -> str:
    client = _get_client()
    
    # Determine which API method to use (default to 'responses')
    api_method = get_env('LLM_METHOD', default='responses').lower()
    
    if api_method == 'responses':
        # Use the newer Responses API
        response = client.responses.create(
            model=get_env('LLM_MODEL'),
            instructions=instructions,
            input=input,
            temperature=0.1
        )
        return response.output_text
        
    elif api_method == 'chat':
        # Use the Chat Completions API
        full_input = f"{instructions}\n\n---\n\nInput Data:\n{input}"
        
        response = client.chat.completions.create(
            model=get_env('LLM_MODEL'),
            messages=[{"role": "user", "content": full_input}],
            temperature=0.1
        )
        return response.choices[0].message.content
```

## Testing Different API Methods

### Test with Responses API
```bash
# Set environment
echo "LLM_METHOD=responses" > .env
echo "LLM_API=https://api.openai.com/v1" >> .env
echo "LLM_KEY=sk-your_key_here" >> .env
echo "LLM_MODEL=gpt-4o-mini" >> .env

# Run test
uv run python test_mvp.py
```

### Test with Chat Completions API
```bash
# Set environment
echo "LLM_METHOD=chat" > .env
echo "LLM_API=https://api.openai.com/v1" >> .env
echo "LLM_KEY=sk-your_key_here" >> .env
echo "LLM_MODEL=gpt-4o-mini" >> .env

# Run test
uv run python test_mvp.py
```

## API Method Comparison

| Feature | Responses API | Chat Completions API |
|---------|---------------|---------------------|
| **Structure** | More structured | Less structured |
| **Instructions** | Separate `instructions` parameter | Combined with input |
| **JSON Output** | Better JSON parsing | May need additional parsing |
| **Cost** | Slightly more expensive | Standard pricing |
| **Model Support** | Most modern models | All models |
| **Reliability** | Newer, may have quirks | Mature, stable |
| **Recommended** | ✅ Yes | ⚠️ If needed |

## Error Handling

If you set an invalid `LLM_METHOD`:

```python
# Invalid value in .env: LLM_METHOD=invalid
# You'll get:
ValueError: Invalid LLM_METHOD: invalid. Must be either 'responses' or 'chat'.
```

## Example Usage

### With Responses API
```python
instructions = "You are a Japanese-Chinese dictionary expert..."
input_data = '{"word": "走る", ...}'
response = get_chat_response(instructions, input_data)
# Uses: client.responses.create(...)
```

### With Chat Completions API
```python
instructions = "You are a Japanese-Chinese dictionary expert..."
input_data = '{"word": "走る", ...}'
response = get_chat_response(instructions, input_data)
# Uses: client.chat.completions.create(...)
# Combines both into: {instructions}\n\n---\n\nInput Data:\n{input_data}
```

## Recommendations

1. **Default to Responses API** (`LLM_METHOD=responses`)
   - Better for structured output
   - More reliable JSON parsing
   - Better suited for dictionary generation

2. **Use Chat API only if:**
   - Your LLM provider doesn't support Responses API
   - You need backwards compatibility
   - You're experiencing issues with Responses API

3. **For Production:**
   - Test both methods with your LLM provider
   - Responses API typically gives better results for dictionary generation
   - Monitor costs and performance

## Provider Compatibility

### OpenAI
- ✅ Responses API: Supported
- ✅ Chat Completions: Supported

### Anthropic (via custom API)
- ⚠️ Responses API: Not officially supported
- ✅ Chat Completions: Use custom endpoint or different client

### Other Providers
- Check provider documentation
- Most support Chat Completions
- Responses API may not be available

## Troubleshooting

### Method Not Supported
```
ValueError: Invalid LLM_METHOD: xxx. Must be either 'responses' or 'chat'.
```
**Solution:** Set `LLM_METHOD=responses` or `LLM_METHOD=chat` in .env

### Chat API Returns Unexpected Format
```
AttributeError: 'NoneType' object has no attribute 'content'
```
**Solution:** Check if your LLM provider supports Chat Completions API

### Responses API Not Available
```
BadRequestError: Invalid request
```
**Solution:** Switch to `LLM_METHOD=chat` in .env

## Summary

✅ Configurable API method via `LLM_METHOD` environment variable  
✅ Default to `responses` (newer, better for structured output)  
✅ Fallback to `chat` for compatibility  
✅ Automatic detection in `get_chat_response()`  
✅ Clear error messages for invalid methods  
✅ Documentation with examples for both methods
