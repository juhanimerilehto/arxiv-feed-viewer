#!/usr/bin/env python3
"""
Daily task to fetch new papers from arXiv and analyze with Grok.
This script should be run by Task Scheduler or cron.
"""
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import SessionLocal
from backend.services.arxiv_service import ArxivService
from backend.services.grok_service import GrokService
from backend.services.paper_service import PaperService
from backend.config import settings

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'daily_fetch.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main fetch routine"""
    logger.info("=" * 80)
    logger.info(f"Daily fetch started at {datetime.now()}")
    logger.info("=" * 80)

    db = SessionLocal()

    try:
        # Initialize services
        arxiv_service = ArxivService()
        grok_service = GrokService(api_key=settings.GROK_API_KEY)
        paper_service = PaperService(arxiv_service, grok_service)

        # Fetch new papers
        papers_added, papers_skipped = await paper_service.fetch_new_papers(
            db=db,
            days_back=settings.ARXIV_DAYS_BACK
        )

        logger.info("=" * 80)
        logger.info(f"Daily fetch completed successfully")
        logger.info(f"Papers added: {papers_added}")
        logger.info(f"Papers skipped: {papers_skipped}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Daily fetch failed with error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
