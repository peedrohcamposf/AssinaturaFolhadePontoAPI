from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_CONNECTION

engine = create_engine(DB_CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()