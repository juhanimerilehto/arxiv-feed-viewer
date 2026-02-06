from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    authors = Column(JSON, nullable=False)  # List of author names
    abstract = Column(Text, nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    updated_date = Column(DateTime, nullable=True)
    pdf_url = Column(String(500), nullable=False)
    pdf_local_path = Column(String(500), nullable=True)
    categories = Column(JSON, nullable=False)  # List of category codes
    primary_category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    grok_analysis = relationship("GrokAnalysis", back_populates="paper", cascade="all, delete-orphan", uselist=False)
    bookmark = relationship("Bookmark", back_populates="paper", cascade="all, delete-orphan", uselist=False)

    __table_args__ = (
        Index('idx_published_date_desc', published_date.desc()),
    )


class GrokAnalysis(Base):
    __tablename__ = "grok_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, unique=True)
    key_points = Column(JSON, nullable=False)  # List of strings (5-7 bullet points)
    summary = Column(Text, nullable=True)  # Optional summary field
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_version = Column(String(50), nullable=False, default="grok-4-1-fast-reasoning")

    # Relationship
    paper = relationship("Paper", back_populates="grok_analysis")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, unique=True)
    bookmarked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationship
    paper = relationship("Paper", back_populates="bookmark")
