"""
Database models for research functionality.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.core.database import Base

class ResearchStatus(str, enum.Enum):
    """Research request status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStep(str, enum.Enum):
    """Workflow step types."""
    INPUT_PARSING = "input_parsing"
    DATA_GATHERING = "data_gathering"
    PROCESSING = "processing"
    RESULT_PERSISTENCE = "result_persistence"
    RETURN_RESULTS = "return_results"

class ResearchRequest(Base):
    """Research request model."""
    
    __tablename__ = "research_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False, index=True)
    status = Column(Enum(ResearchStatus), default=ResearchStatus.PENDING, index=True)
    task_id = Column(String(100), unique=True, index=True)  # Celery task ID
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    logs = relationship("WorkflowLog", back_populates="research_request", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="research_request", cascade="all, delete-orphan")

class WorkflowLog(Base):
    """Workflow execution logs."""
    
    __tablename__ = "workflow_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    research_request_id = Column(Integer, ForeignKey("research_requests.id"), nullable=False)
    step = Column(Enum(WorkflowStep), nullable=False)
    status = Column(String(20), nullable=False)  # started, completed, failed
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Relationships
    research_request = relationship("ResearchRequest", back_populates="logs")

class Article(Base):
    """Extracted articles."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    research_request_id = Column(Integer, ForeignKey("research_requests.id"), nullable=False)
    
    # Article data
    title = Column(String(500), nullable=False)
    url = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)  # wikipedia, hackernews, etc.
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # List of extracted keywords
    
    # Metadata
    published_at = Column(DateTime(timezone=True), nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    relevance_score = Column(Integer, default=0)  # 0-100
    
    # Relationships
    research_request = relationship("ResearchRequest", back_populates="articles")