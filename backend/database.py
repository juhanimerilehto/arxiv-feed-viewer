from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.models import Base

# Create engine
engine = create_engine(
    settings.get_database_url(),
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and FTS5 virtual table"""
    Base.metadata.create_all(bind=engine)

    # Create FTS5 virtual table for full-text search
    with engine.connect() as conn:
        # Check if FTS table already exists
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='papers_fts'")
        )
        if result.fetchone() is None:
            # Create FTS5 virtual table
            conn.execute(text("""
                CREATE VIRTUAL TABLE papers_fts USING fts5(
                    arxiv_id,
                    title,
                    abstract,
                    content='papers',
                    content_rowid='id'
                )
            """))

            # Create triggers to keep FTS in sync with papers table
            conn.execute(text("""
                CREATE TRIGGER papers_fts_insert AFTER INSERT ON papers BEGIN
                    INSERT INTO papers_fts(rowid, arxiv_id, title, abstract)
                    VALUES (new.id, new.arxiv_id, new.title, new.abstract);
                END
            """))

            conn.execute(text("""
                CREATE TRIGGER papers_fts_update AFTER UPDATE ON papers BEGIN
                    UPDATE papers_fts SET
                        arxiv_id = new.arxiv_id,
                        title = new.title,
                        abstract = new.abstract
                    WHERE rowid = new.id;
                END
            """))

            conn.execute(text("""
                CREATE TRIGGER papers_fts_delete AFTER DELETE ON papers BEGIN
                    DELETE FROM papers_fts WHERE rowid = old.id;
                END
            """))

            conn.commit()
            print("FTS5 virtual table and triggers created successfully")
