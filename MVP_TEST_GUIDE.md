# MVP Test Script Guide

## Overview
The `test_mvp.py` script is a minimal test to verify that your Japanese-Chinese dictionary conversion works correctly. It processes 2 sample Japanese words and generates Chinese definitions using the LLM.

## Quick Start

### 1. Install Dependencies
```bash
cd /d/open-dictionary-ja
uv sync
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your DATABASE_URL
# Or add your LLM provider API keys (OpenAI, Anthropic, etc.)
```

### 3. Run the Test
```bash
# Basic run
python test_mvp.py

# Or with uv
uv run python test_mvp.py
```

## What It Does

1. **Loads Environment Variables** - Reads .env file if present
2. **Fetches 2 Mock Japanese Entries**:
   - `走る` (hashiru - to run)
   - `おもてなし` (omotenashi - hospitality)
3. **Generates Definitions** - Uses LLM to create Japanese-Chinese definitions
4. **Outputs Results**:
   - `data/mvp_test_output.json` - Pretty-printed JSON
   - `data/mvp_test_output.jsonl` - One definition per line

## Sample Output

### Input (Mock Data)
```json
{
  "word": "走る",
  "pos": "verb",
  "senses": [{"glosses": ["To run; to move quickly on foot."]}],
  "forms": [{"form": "走ります", "tags": ["polite", "present"]}],
  "sounds": [{"ipa": "/haɕiɾu/", "ogg_url": null}],
  "derived": [{"word": "走者"}],
  "etymology_text": "From Old Japanese *pay- ('to fly, to jump')"
}
```

### Output (Generated)
```json
[
  {
    "word": "走る",
    "pos": "verb",
    "pronunciations": {
      "ipa": "/haɕiɾu/",
      "natural_phonics": "はしる",
      "ogg_url": null
    },
    "forms": [
      "走ります (丁寧語)",
      "走った (过去式)",
      "走って (て形)"
    ],
    "concise_definition": "奔跑；逃跑。",
    "detailed_definitions": [
      {
        "definition_en": "To run; to move quickly on foot.",
        "definition_cn": "指人或动物用双脚快速移动的动作，强调速度。日常使用频率很高的基础动词。",
        "example": {
          "ja": "私は每天朝公園を走ります。",
          "cn": "我每天早上在公园跑步。"
        }
      }
    ],
    "derived": [
      {
        "word": "走者",
        "definition_cn": "跑步者，赛跑运动员。"
      }
    ],
    "etymology": "该词源自古代日语的 *pay-（意为'飞翔，跳动'），最终源于原始日语 *paya。从古至今核心含义一直围绕着'快速移动'这一概念。"
  }
]
```

## Configuration

### .env File
Copy `.env.example` to `.env` and configure:

```bash
# Required for database operations
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Optional - for LLM generation
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### LLM Client Setup
The script uses `open_dictionary.llm.llm_client.get_chat_response()` which should be configured with your LLM provider.

If you don't have a database or LLM set up, the script will still work with mock data.

## Output Files

### JSON Format (`data/mvp_test_output.json`)
Pretty-printed with indentation, easy to read:
```json
[
  {
    "word": "...",
    ...
  }
]
```

### JSONL Format (`data/mvp_test_output.jsonl`)
One JSON object per line, compact and streaming-friendly:
```json
{"word": "...", ...}
{"word": "...", ...}
```

## Testing with Real Database Data

To test with real database entries instead of mock data, modify the `fetch_japanese_entries()` function:

```python
def fetch_japanese_entries(limit: int = 2) -> List[Dict[str, Any]]:
    """Fetch Japanese dictionary entries from PostgreSQL."""
    try:
        conninfo = os.getenv("DATABASE_URL")
        if not conninfo:
            raise RuntimeError("DATABASE_URL not set")
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT data FROM dictionary_filtered_ja
                    WHERE data ? 'word'
                    LIMIT %s
                """, (limit,))
                
                results = []
                for row in cur:
                    results.append(row[0])
                return results
    except Exception as e:
        print(f"⚠️  Database fetch failed: {e}")
        print("   Using mock data instead...")
        # Fall back to mock data
        ...
```

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /d/open-dictionary-ja
python test_mvp.py
```

### LLM API Errors
- Check your API keys in .env
- Verify LLM client configuration in `src/open_dictionary/llm/llm_client.py`
- Check rate limits and quotas

### Database Connection Errors
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database and tables exist

## Next Steps

After verifying the test works:
1. Scale up: Process more entries (change `limit=2` to `limit=100`)
2. Use real database data instead of mock data
3. Integrate into the full pipeline with `uv run open-dictionary define`

## Files Created

- ✅ `test_mvp.py` - Executable test script
- ✅ `.env.example` - Environment template
- ✅ `MVP_TEST_GUIDE.md` - This guide
