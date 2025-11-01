from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://mcp_user:mcp_pass@localhost:5432/mcp_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserInput(Base):
    """Model pentru stocarea inputurilor utilizatorilor"""
    __tablename__ = "user_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserInput(id={self.id}, session={self.session_id}, timestamp={self.timestamp})>"


def init_db():
    """Inițializează baza de date și creează tabelele"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency pentru obținerea sesiunii de bază de date"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
