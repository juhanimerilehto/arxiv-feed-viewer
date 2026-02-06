#!/usr/bin/env python3
"""
Add Grok analysis to papers that don't have it yet
"""
import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.models import Paper, GrokAnalysis
from backend.services.grok_service import GrokService
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Add Grok analysis to papers missing it"""
    print("=" * 80)
    print("Adding Grok analysis to papers without it")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Find papers without Grok analysis
        papers_without_analysis = db.query(Paper)\
            .outerjoin(GrokAnalysis)\
            .filter(GrokAnalysis.id == None)\
            .all()

        if not papers_without_analysis:
            print("\nAll papers already have Grok analysis!")
            return

        print(f"\nFound {len(papers_without_analysis)} papers without analysis")

        # Initialize Grok service
        grok = GrokService(api_key=settings.GROK_API_KEY)
        logger.info(f"Using Grok model: {grok.model}")

        analyzed = 0
        failed = 0

        for paper in papers_without_analysis:
            print(f"\nAnalyzing: {paper.title[:60]}...")

            try:
                # Analyze with Grok
                key_points = await grok.analyze_paper(
                    title=paper.title,
                    abstract=paper.abstract
                )

                if key_points:
                    # Create analysis record
                    analysis = GrokAnalysis(
                        paper_id=paper.id,
                        key_points=key_points,
                        model_version=grok.model
                    )
                    db.add(analysis)
                    db.commit()

                    analyzed += 1
                    print(f"  -> Added {len(key_points)} key points")
                else:
                    failed += 1
                    logger.warning(f"No analysis returned for paper {paper.id}")

            except Exception as e:
                failed += 1
                logger.error(f"Failed to analyze paper {paper.id}: {e}")
                db.rollback()

        print("\n" + "=" * 80)
        print(f"Analysis complete!")
        print(f"  Analyzed: {analyzed}")
        print(f"  Failed: {failed}")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
