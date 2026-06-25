from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import settings

Base = declarative_base()


class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, unique=True, nullable=False, index=True)
    last_checked_commit = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    code_changes = relationship("CodeChange", back_populates="repository")


class CodeChange(Base):
    __tablename__ = "code_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    commit_hash = Column(String, nullable=False, index=True)
    branch = Column(String, nullable=False)
    author = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    repository = relationship("Repository", back_populates="code_changes")
    analysis_results = relationship("AnalysisResult", back_populates="code_change", uselist=False)
    pr_request = relationship("PRRequest", back_populates="code_change", uselist=False)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("code_changes.id"), nullable=False, unique=True)
    issues_found = Column(JSON, nullable=False)
    suggestions = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    code_change = relationship("CodeChange", back_populates="analysis_results")


class PRRequest(Base):
    __tablename__ = "pr_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("code_changes.id"), nullable=False, unique=True)
    status = Column(String, nullable=False)
    approval_timestamp = Column(DateTime, nullable=True)
    pr_url = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    code_change = relationship("CodeChange", back_populates="pr_request")


class AgentState(Base):
    __tablename__ = "agent_state"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, nullable=False, index=True)
    state_data = Column(JSON, nullable=False)
    checkpoint = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)


DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
