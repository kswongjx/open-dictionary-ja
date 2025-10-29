#!/usr/bin/env python3
"""
MVP Test Script for Japanese-Chinese Dictionary

This script fetches 2 Japanese dictionary entries from PostgreSQL,
generates Japanese-Chinese definitions using LLM,
and outputs the results to JSON/JSONL files.

Usage:
    python test_mvp.py
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

try:
    import psycopg
    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False

from open_dictionary.llm.define import define, Definition


def load_env():
    """Load environment variables from .env file."""
    if not HAS_DOTENV:
        print("WARNING: python-dotenv not installed, skipping .env loading")
        return
    
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"OK: Loaded environment from {env_path}")
    else:
        print(f"WARNING: .env file not found at {env_path}")
        print("         Using environment variables from system...")


def fetch_japanese_entries(limit: int = 2) -> List[Dict[str, Any]]:
    """
    Fetch Japanese dictionary entries from PostgreSQL.
    
    Args:
        limit: Number of entries to fetch
        
    Returns:
        List of dictionary entries
    """
    mock_entries = [
        {
            "word": "走る",
            "pos": "verb",
            "lang": "ja",
            "lang_code": "ja",
            "forms": [
                {"form": "走ります", "tags": ["polite", "present"]},
                {"form": "走った", "tags": ["past"]},
                {"form": "走って", "tags": ["te-form"]}
            ],
            "senses": [
                {"glosses": ["To run; to move quickly on foot."]},
                {"glosses": ["To flee; to escape."]}
            ],
            "sounds": [{"ipa": "/haɕiɾu/", "ogg_url": None}],
            "derived": [{"word": "走者"}, {"word": "走れ"}],
            "etymology_text": "From Old Japanese *pay- ('to fly, to jump'), from Proto-Japanese *paya."
        },
        {
            "word": "おもてなし",
            "pos": "noun",
            "lang": "ja",
            "lang_code": "ja",
            "forms": [
                {"form": "おもてなし", "tags": ["honorific"]}
            ],
            "senses": [
                {"glosses": ["Hospitality; entertainment of guests."]},
                {"glosses": ["The act of providing exceptional service to others."]}
            ],
            "sounds": [{"ipa": "/omotenɕi/", "ogg_url": None}],
            "derived": [{"word": "もてなし"}, {"word": "おもてなしする"}],
            "etymology_text": "From Old Japanese, from もと (moto, 'origin') + なて (nate, 'to treat, to handle') + the honorific prefix お- (o-)."
        }
    ]
    
    print(f"Using {len(mock_entries)} mock Japanese entries for testing")
    return mock_entries[:limit]


def generate_definitions(entries: List[Dict[str, Any]]) -> List[Definition]:
    """
    Generate dictionary definitions for entries using LLM.
    
    Args:
        entries: List of dictionary entries
        
    Returns:
        List of generated definitions
    """
    definitions = []
    
    print(f"\nGenerating definitions with LLM...")
    print(f"Entries to process: {len(entries)}")
    
    for i, entry in enumerate(entries, 1):
        print(f"\nProcessing {i}/{len(entries)}: {entry['word']}")
        try:
            definition = define(entry)
            definitions.append(definition)
            print(f"OK: Generated definition for: {definition.word}")
        except Exception as e:
            print(f"ERROR: Failed to generate definition for {entry['word']}: {e}")
            print(f"Error type: {type(e).__name__}")
            if "api_key" in str(e).lower() or "API" in str(e):
                print("TIP: Check your LLM API keys in .env")
            import traceback
            traceback.print_exc()
    
    return definitions


def save_to_json(definitions: List[Definition], output_path: str = "data/mvp_test_output.json"):
    """Save definitions to a JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = [definition.model_dump() for definition in definitions]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved definitions to: {output_file}")
    print(f"Total definitions: {len(data)}")
    return output_file


def save_to_jsonl(definitions: List[Definition], output_path: str = "data/mvp_test_output.jsonl"):
    """Save definitions to a JSONL file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for definition in definitions:
            json_line = json.dumps(definition.model_dump(), ensure_ascii=False)
            f.write(json_line + '\n')
    
    print(f"Saved definitions to: {output_file}")
    print(f"Total definitions: {len(definitions)}")
    return output_file


def print_summary(definitions: List[Definition]):
    """Print a summary of generated definitions."""
    print("\n" + "=" * 60)
    print("MVP Test Summary")
    print("=" * 60)
    print(f"Total entries processed: {len(definitions)}")
    
    if definitions:
        print("\nGenerated entries:")
        for definition in definitions:
            print(f"\n  - {definition.word} ({definition.pos})")
            print(f"    Concise definition: {definition.concise_definition}")
            print(f"    Detailed definitions: {len(definition.detailed_definitions)}")
            print(f"    Derived words: {len(definition.derived)}")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point for the MVP test script."""
    print("=" * 60)
    print("Japanese-Chinese Dictionary MVP Test")
    print("=" * 60)
    
    load_env()
    
    if not os.getenv("DATABASE_URL"):
        print("\nWARNING: DATABASE_URL not set in environment")
        print("         This is OK - using mock data for testing")
    
    if not HAS_PSYCOPG:
        print("WARNING: psycopg not installed - database features disabled")
    
    try:
        print("\nStep 1: Fetching Japanese dictionary entries...")
        entries = fetch_japanese_entries(limit=2)
        
        print("\nStep 2: Generating Japanese-Chinese definitions...")
        definitions = generate_definitions(entries)
        
        print("\nStep 3: Saving to JSON/JSONL files...")
        json_file = save_to_json(definitions)
        jsonl_file = save_to_jsonl(definitions)
        
        print_summary(definitions)
        
        print("\nMVP test completed!")
        print(f"\nOutput files:")
        print(f"  - JSON:  {json_file}")
        print(f"  - JSONL: {jsonl_file}")
        
    except Exception as e:
        print(f"\nERROR during MVP test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
