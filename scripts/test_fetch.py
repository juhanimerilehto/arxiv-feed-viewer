#!/usr/bin/env python3
"""
Test script to fetch a few papers from arXiv and analyze with Grok.
This fetches only 5 papers for testing purposes.
"""
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.services.arxiv_service import ArxivService
from backend.services.grok_service import GrokService
from backend.services.paper_service import PaperService
from backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    """Fetch a small set of papers for testing"""
    print("=" * 80)
    print("TEST FETCH - Fetching 5 papers from last 7 days")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Initialize services
        arxiv_service = ArxivService()
        grok_service = GrokService(api_key=settings.GROK_API_KEY)
        paper_service = PaperService(arxiv_service, grok_service)

        # Temporarily override max results
        original_max = settings.ARXIV_MAX_RESULTS
        settings.ARXIV_MAX_RESULTS = 5

        # Fetch papers
        papers_added, papers_skipped = await paper_service.fetch_new_papers(
            db=db,
            days_back=7
        )

        # Restore original max
        settings.ARXIV_MAX_RESULTS = original_max

        print("=" * 80)
        print(f"Test fetch completed!")
        print(f"Papers added: {papers_added}")
        print(f"Papers skipped: {papers_skipped}")
        print("=" * 80)
        print("\nYou can now open http://127.0.0.1:8000 in your browser to view the papers!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
