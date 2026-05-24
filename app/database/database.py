from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use SQLite by default for easier local setup if Postgres is not available.
# Override with DATABASE_URL for PostgreSQL as requested.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expense_tracker.db")

# SQLite needs connect_args={"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Postgres
    # Ensure correct dialect for sqlalchemy (postgres -> postgresql)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
