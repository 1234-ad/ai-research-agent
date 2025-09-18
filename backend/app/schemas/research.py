"""
Pydantic schemas for research functionality.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ResearchStatus(str, Enum):
    """Research request status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStep(str, Enum):
    """Workflow step types."""
    INPUT_PARSING = "input_parsing"
    DATA_GATHERING = "data_gathering"
    PROCESSING = "processing"
    RESULT_PERSISTENCE = "result_persistence"
    RETURN_RESULTS = "return_results"

# Request schemas
class ResearchRequestCreate(BaseModel):
    """Schema for creating a research request."""
    topic: str = Field(..., min_length=3, max_length=500, description="Research topic")

class ResearchRequestUpdate(BaseModel):
    """Schema for updating a research request."""
    status: Optional[ResearchStatus] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# Response schemas
class ArticleResponse(BaseModel):
    """Schema for article response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    url: Optional[str] = None
    source: str
    content: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    published_at: Optional[datetime] = None
    extracted_at: datetime
    relevance_score: int

class WorkflowLogResponse(BaseModel):
    """Schema for workflow log response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    step: WorkflowStep
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

class ResearchRequestResponse(BaseModel):
    """Schema for research request response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    topic: str
    status: ResearchStatus
    task_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ResearchRequestDetailResponse(ResearchRequestResponse):
    """Schema for detailed research request response."""
    logs: List[WorkflowLogResponse] = []
    articles: List[ArticleResponse] = []

class ResearchRequestListResponse(BaseModel):
    """Schema for research request list response."""
    items: List[ResearchRequestResponse]
    total: int
    page: int
    size: int
    pages: int

# WebSocket schemas
class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str
    data: Dict[str, Any]

class ProgressUpdate(BaseModel):
    """Schema for progress updates."""
    step: WorkflowStep
    status: str
    message: str
    progress: int = Field(..., ge=0, le=100)
    details: Optional[Dict[str, Any]] = None

# Results schemas
class ResearchResults(BaseModel):
    """Schema for final research results."""
    topic: str
    summary: str
    top_articles: List[ArticleResponse]
    keywords: List[str]
    sources: List[str]
    total_articles_found: int
    processing_time_ms: int
    completed_at: datetime