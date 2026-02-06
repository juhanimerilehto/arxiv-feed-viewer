import arxiv
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ArxivService:
    def __init__(self, rate_limit_delay: float = 3.0):
        """
        Initialize arXiv service with rate limiting.

        Args:
            rate_limit_delay: Seconds to wait between requests (default 3.0)
        """
        self.rate_limit_delay = rate_limit_delay
        self.client = arxiv.Client()

    def search_papers(
        self,
        query: str,
        max_results: int = 50,
        days_back: int = 7
    ) -> List[arxiv.Result]:
        """
        Search arXiv for papers matching query within date range.

        Args:
            query: arXiv API search query
            max_results: Maximum number of results to return
            days_back: How many days back to search

        Returns:
            List of arxiv.Result objects
        """
        # Calculate date range (timezone-aware)
        from datetime import timezone
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)

        logger.info(f"Searching arXiv: query='{query}', max_results={max_results}, "
                   f"date_range={start_date.date()} to {end_date.date()}")

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        results = []
        for result in self.client.results(search):
            # Filter by date range (published or updated)
            paper_date = result.updated if result.updated else result.published

            # Make paper_date timezone-aware if it isn't already
            if paper_date.tzinfo is None:
                paper_date = paper_date.replace(tzinfo=timezone.utc)

            if paper_date >= start_date:
                results.append(result)

        logger.info(f"Found {len(results)} papers matching criteria")
        return results

    def download_pdf(
        self,
        paper: arxiv.Result,
        save_dir: Path
    ) -> Optional[Path]:
        """
        Download PDF for a paper to local storage.

        Args:
            paper: arXiv result object
            save_dir: Directory to save PDFs

        Returns:
            Path to downloaded PDF or None if failed
        """
        try:
            # Sanitize arxiv_id for filename (replace / and : with _)
            safe_id = paper.get_short_id().replace("/", "_").replace(":", "_")
            pdf_filename = f"{safe_id}.pdf"
            pdf_path = save_dir / pdf_filename

            # Skip if already downloaded
            if pdf_path.exists():
                logger.info(f"PDF already exists: {pdf_path}")
                return pdf_path

            # Download with rate limiting
            logger.info(f"Downloading PDF: {paper.title[:50]}...")
            paper.download_pdf(dirpath=str(save_dir), filename=pdf_filename)
            time.sleep(self.rate_limit_delay)  # Rate limiting

            if pdf_path.exists():
                logger.info(f"Successfully downloaded: {pdf_path}")
                return pdf_path
            else:
                logger.error(f"PDF download failed (file not found): {paper.get_short_id()}")
                return None

        except Exception as e:
            logger.error(f"Error downloading PDF for {paper.get_short_id()}: {e}")
            return None
