from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import config

engine = create_engine(
    url=config.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind = engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()