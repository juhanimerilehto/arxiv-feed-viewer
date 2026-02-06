import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from typing import List, Optional, Tuple
from datetime import datetime

from backend.models import Paper, GrokAnalysis, Bookmark
from backend.services.arxiv_service import ArxivService
from backend.services.grok_service import GrokService
from backend.config import settings

logger = logging.getLogger(__name__)


class PaperService:
    def __init__(self, arxiv_service: ArxivService, grok_service: GrokService):
        self.arxiv_service = arxiv_service
        self.grok_service = grok_service

    async def fetch_new_papers(self, db: Session, days_back: int = 7) -> Tuple[int, int]:
        """
        Fetch new papers from arXiv, analyze with Grok, and store in database.

        Args:
            db: Database session
            days_back: How many days back to search

        Returns:
            Tuple of (papers_added, papers_skipped)
        """
        papers_added = 0
        papers_skipped = 0

        try:
            # Search arXiv
            results = self.arxiv_service.search_papers(
                query=settings.ARXIV_SEARCH_QUERY,
                max_results=settings.ARXIV_MAX_RESULTS,
                days_back=days_back
            )

            logger.info(f"Processing {len(results)} papers from arXiv")

            for arxiv_paper in results:
                arxiv_id = arxiv_paper.get_short_id()

                # Check if already exists
                existing = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
                if existing:
                    logger.debug(f"Paper already exists: {arxiv_id}")
                    papers_skipped += 1
                    continue

                # Download PDF
                pdf_storage = settings.get_pdf_storage_path()
                pdf_path = self.arxiv_service.download_pdf(arxiv_paper, pdf_storage)

                # Create paper record
                paper = Paper(
                    arxiv_id=arxiv_id,
                    title=arxiv_paper.title,
                    authors=[author.name for author in arxiv_paper.authors],
                    abstract=arxiv_paper.summary,
                    published_date=arxiv_paper.published,
                    updated_date=arxiv_paper.updated,
                    pdf_url=arxiv_paper.pdf_url,
                    pdf_local_path=str(pdf_path) if pdf_path else None,
                    categories=[cat for cat in arxiv_paper.categories],
                    primary_category=arxiv_paper.primary_category
                )

                db.add(paper)
                db.flush()  # Get paper.id

                # Analyze with Grok
                try:
                    key_points = await self.grok_service.analyze_paper(
                        title=paper.title,
                        abstract=paper.abstract
                    )

                    if key_points:
                        analysis = GrokAnalysis(
                            paper_id=paper.id,
                            key_points=key_points,
                            model_version=self.grok_service.model
                        )
                        db.add(analysis)
                        logger.info(f"Added paper with Grok analysis: {arxiv_id}")
                    else:
                        logger.warning(f"Grok analysis failed for {arxiv_id}, paper added without analysis")

                except Exception as e:
                    logger.error(f"Grok analysis error for {arxiv_id}: {e}")

                db.commit()
                papers_added += 1

            logger.info(f"Fetch complete: {papers_added} added, {papers_skipped} skipped")
            return papers_added, papers_skipped

        except Exception as e:
            logger.error(f"Error in fetch_new_papers: {e}")
            db.rollback()
            raise

    def get_papers(
        self,
        db: Session,
        limit: int = 20,
        offset: int = 0,
        bookmarked_only: bool = False
    ) -> Tuple[List[Paper], int]:
        """
        Get paginated list of papers, newest first.

        Args:
            db: Database session
            limit: Number of papers to return
            offset: Offset for pagination
            bookmarked_only: If True, only return bookmarked papers

        Returns:
            Tuple of (papers list, total count)
        """
        query = db.query(Paper)

        if bookmarked_only:
            query = query.join(Bookmark)

        total = query.count()

        papers = query.order_by(desc(Paper.published_date))\
                     .limit(limit)\
                     .offset(offset)\
                     .all()

        return papers, total

    def get_paper_by_id(self, db: Session, paper_id: int) -> Optional[Paper]:
        """Get single paper by ID with all relationships loaded"""
        return db.query(Paper).filter(Paper.id == paper_id).first()

    def search_papers(self, db: Session, query: str, limit: int = 20) -> List[Paper]:
        """
        Full-text search papers using FTS5.

        Args:
            db: Database session
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching papers
        """
        # Use FTS5 MATCH query
        sql = text("""
            SELECT papers.*
            FROM papers
            JOIN papers_fts ON papers.id = papers_fts.rowid
            WHERE papers_fts MATCH :query
            ORDER BY papers.published_date DESC
            LIMIT :limit
        """)

        result = db.execute(sql, {"query": query, "limit": limit})
        paper_ids = [row[0] for row in result]

        # Fetch full paper objects
        papers = db.query(Paper).filter(Paper.id.in_(paper_ids)).all()

        # Sort by published_date desc
        papers.sort(key=lambda p: p.published_date, reverse=True)

        return papers

    def is_bookmarked(self, db: Session, paper_id: int) -> bool:
        """Check if a paper is bookmarked"""
        bookmark = db.query(Bookmark).filter(Bookmark.paper_id == paper_id).first()
        return bookmark is not None
