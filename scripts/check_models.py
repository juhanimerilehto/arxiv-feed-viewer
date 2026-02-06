#!/usr/bin/env python3
"""
Check available Grok models
"""
import sys
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings

def main():
    print("Checking available Grok models...")
    print(f"API Key: {settings.GROK_API_KEY[:20]}...")

    # Try to get list of models
    url = "https://api.x.ai/v1/language-models"

    try:
        response = httpx.get(
            url,
            headers={
                "Authorization": f"Bearer {settings.GROK_API_KEY}"
            },
            timeout=30.0
        )

        print(f"\nStatus: {response.status_code}")
        print(f"Response:\n{response.text}\n")

        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print("Available models:")
                for model in data["data"]:
                    print(f"  - {model.get('id', 'unknown')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
