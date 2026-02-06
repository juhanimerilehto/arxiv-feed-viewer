from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class GrokAnalysisSchema(BaseModel):
    key_points: List[str]
    summary: Optional[str] = None
    analyzed_at: datetime
    model_version: str

    class Config:
        from_attributes = True


class BookmarkSchema(BaseModel):
    id: int
    bookmarked_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class PaperBase(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: datetime
    updated_date: Optional[datetime] = None
    pdf_url: str
    categories: List[str]
    primary_category: str


class PaperList(PaperBase):
    id: int
    is_bookmarked: bool = False

    class Config:
        from_attributes = True


class PaperDetail(PaperBase):
    id: int
    pdf_local_path: Optional[str] = None
    grok_analysis: Optional[GrokAnalysisSchema] = None
    bookmark: Optional[BookmarkSchema] = None
    is_bookmarked: bool = False

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    papers: List[PaperList]
    total: int
    limit: int
    offset: int


class BookmarkCreate(BaseModel):
    paper_id: int
    notes: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: int
    paper_id: int
    bookmarked_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
