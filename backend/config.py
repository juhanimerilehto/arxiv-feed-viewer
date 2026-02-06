from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    GROK_API_KEY: str
    DATABASE_PATH: str = "data/arxiv.db"
    PDF_STORAGE_PATH: str = "data/pdfs"
    ARXIV_SEARCH_QUERY: str = 'cat:cs.CR AND (abs:LLM OR abs:"Large Language Model" OR abs:"Generative AI" OR abs:GenAI)'
    ARXIV_MAX_RESULTS: int = 10
    ARXIV_DAYS_BACK: int = 7
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_url(self) -> str:
        """Get SQLite database URL"""
        db_path = Path(self.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    def get_pdf_storage_path(self) -> Path:
        """Get PDF storage directory as Path object"""
        pdf_path = Path(self.PDF_STORAGE_PATH)
        pdf_path.mkdir(parents=True, exist_ok=True)
        return pdf_path


settings = Settings()
