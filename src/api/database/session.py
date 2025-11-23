from typing import Generator
from sqlalchemy.orm import Session

from src.api.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    This function is used as a FastAPI dependency to provide
    a database session to route handlers. It ensures that:
    1. A new session is created for each request
    2. The session is properly closed after the request

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/properties")
        def get_properties(db: Session = Depends(get_db)):
            # db is now available for database operations
            return db.query(Property).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
