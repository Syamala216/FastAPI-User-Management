from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL Database URL
SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg2://postgres:Sya12%4034@localhost:5432/fastapi_db"
)

# Create Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()