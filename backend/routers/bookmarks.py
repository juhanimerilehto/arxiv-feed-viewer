from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.schemas import BookmarkCreate, BookmarkResponse, PaperList
from backend.models import Bookmark, Paper

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.post("/", response_model=BookmarkResponse, status_code=201)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db)
):
    """
    Add a bookmark for a paper.

    Args:
        bookmark_data: Bookmark creation data
        db: Database session
    """
    # Check if paper exists
    paper = db.query(Paper).filter(Paper.id == bookmark_data.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Check if already bookmarked
    existing = db.query(Bookmark).filter(Bookmark.paper_id == bookmark_data.paper_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Paper already bookmarked")

    # Create bookmark
    bookmark = Bookmark(
        paper_id=bookmark_data.paper_id,
        notes=bookmark_data.notes
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return bookmark


@router.delete("/{paper_id}", status_code=204)
def delete_bookmark(paper_id: int, db: Session = Depends(get_db)):
    """
    Remove a bookmark for a paper.

    Args:
        paper_id: Paper ID
        db: Database session
    """
    bookmark = db.query(Bookmark).filter(Bookmark.paper_id == paper_id).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()

    return None


@router.get("/", response_model=List[PaperList])
def list_bookmarks(db: Session = Depends(get_db)):
    """
    Get all bookmarked papers.

    Args:
        db: Database session
    """
    bookmarks = db.query(Bookmark).all()
    papers = [bookmark.paper for bookmark in bookmarks]

    # Convert to response schema
    paper_list = []
    for paper in papers:
        paper_dict = PaperList.model_validate(paper).model_dump()
        paper_dict["is_bookmarked"] = True
        paper_list.append(PaperList(**paper_dict))

    return paper_list
