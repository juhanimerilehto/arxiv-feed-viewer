#!/usr/bin/env python3
"""
Test script to verify Grok API is working
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.grok_service import GrokService
from backend.config import settings

async def main():
    print("Testing Grok API...")
    print(f"API Key: {settings.GROK_API_KEY[:20]}...")

    grok = GrokService(api_key=settings.GROK_API_KEY)
    print(f"Using model: {grok.model}")
    print(f"Endpoint: {grok.base_url}")

    # Test with a simple paper
    title = "Secure Tool Manifest and Digital Signing Solution"
    abstract = "Large Language Models (LLMs) are increasingly adopted in sensitive domains. This paper proposes a framework for secure implementation."

    print("\nAnalyzing test paper...")
    try:
        key_points = await grok.analyze_paper(title, abstract)

        if key_points:
            print("\n[SUCCESS] Grok API is working!")
            print(f"\nExtracted {len(key_points)} key points:")
            for i, point in enumerate(key_points, 1):
                print(f"  {i}. {point}")
        else:
            print("\n[FAILED] No key points returned")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
