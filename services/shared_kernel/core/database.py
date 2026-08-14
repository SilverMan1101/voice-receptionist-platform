import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Default to Postgres locally if not provided
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://receptionist_user:receptionist_password@localhost:5432/receptionist_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
