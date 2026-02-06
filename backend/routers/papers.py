from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.schemas import PaperListResponse, PaperDetail, PaperList
from backend.services.paper_service import PaperService
from backend.services.arxiv_service import ArxivService
from backend.services.grok_service import GrokService
from backend.config import settings

router = APIRouter(prefix="/api/papers", tags=["papers"])

# Initialize services
arxiv_service = ArxivService()
grok_service = GrokService(api_key=settings.GROK_API_KEY)
paper_service = PaperService(arxiv_service, grok_service)


@router.get("/", response_model=PaperListResponse)
def list_papers(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    bookmarked: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of papers, newest first.

    Args:
        limit: Number of papers per page (1-100)
        offset: Offset for pagination
        bookmarked: If true, only return bookmarked papers
        db: Database session
    """
    papers, total = paper_service.get_papers(db, limit, offset, bookmarked)

    # Convert to response schema with bookmark status
    paper_list = []
    for paper in papers:
        paper_dict = PaperList.model_validate(paper).model_dump()
        paper_dict["is_bookmarked"] = paper.bookmark is not None
        paper_list.append(PaperList(**paper_dict))

    return PaperListResponse(
        papers=paper_list,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/search", response_model=List[PaperList])
def search_papers(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Full-text search papers by keyword.

    Args:
        q: Search query string
        limit: Maximum number of results
        db: Database session
    """
    papers = paper_service.search_papers(db, q, limit)

    # Convert to response schema with bookmark status
    paper_list = []
    for paper in papers:
        paper_dict = PaperList.model_validate(paper).model_dump()
        paper_dict["is_bookmarked"] = paper.bookmark is not None
        paper_list.append(PaperList(**paper_dict))

    return paper_list


@router.get("/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """
    Get single paper by ID with Grok analysis.

    Args:
        paper_id: Paper ID
        db: Database session
    """
    paper = paper_service.get_paper_by_id(db, paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Convert to response schema with bookmark status
    paper_dict = PaperDetail.model_validate(paper).model_dump()
    paper_dict["is_bookmarked"] = paper.bookmark is not None

    return PaperDetail(**paper_dict)
