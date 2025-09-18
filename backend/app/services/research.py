"""
Research service for database operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.research import ResearchRequest, WorkflowLog, Article, ResearchStatus, WorkflowStep
from app.schemas.research import (
    ResearchRequestResponse,
    ResearchRequestDetailResponse,
    WorkflowLogResponse,
    ArticleResponse
)

class ResearchService:
    """Service for research-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_research_request(self, topic: str) -> ResearchRequestResponse:
        """Create a new research request."""
        research_request = ResearchRequest(
            topic=topic,
            status=ResearchStatus.PENDING
        )
        
        self.db.add(research_request)
        self.db.commit()
        self.db.refresh(research_request)
        
        return ResearchRequestResponse.model_validate(research_request)
    
    def update_task_id(self, request_id: int, task_id: str) -> ResearchRequestResponse:
        """Update research request with Celery task ID."""
        research_request = self.db.query(ResearchRequest).filter(
            ResearchRequest.id == request_id
        ).first()
        
        if research_request:
            research_request.task_id = task_id
            self.db.commit()
            self.db.refresh(research_request)
        
        return ResearchRequestResponse.model_validate(research_request)
    
    def update_status(self, request_id: int, status: ResearchStatus, 
                     results: dict = None, error_message: str = None) -> Optional[ResearchRequestResponse]:
        """Update research request status and results."""
        research_request = self.db.query(ResearchRequest).filter(
            ResearchRequest.id == request_id
        ).first()
        
        if not research_request:
            return None
        
        research_request.status = status
        if results:
            research_request.results = results
        if error_message:
            research_request.error_message = error_message
        if status == ResearchStatus.COMPLETED:
            research_request.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(research_request)
        
        return ResearchRequestResponse.model_validate(research_request)
    
    def get_research_request(self, request_id: int) -> Optional[ResearchRequestResponse]:
        """Get a research request by ID."""
        research_request = self.db.query(ResearchRequest).filter(
            ResearchRequest.id == request_id
        ).first()
        
        if not research_request:
            return None
        
        return ResearchRequestResponse.model_validate(research_request)
    
    def get_research_request_detail(self, request_id: int) -> Optional[ResearchRequestDetailResponse]:
        """Get detailed research request with logs and articles."""
        research_request = self.db.query(ResearchRequest).filter(
            ResearchRequest.id == request_id
        ).first()
        
        if not research_request:
            return None
        
        return ResearchRequestDetailResponse.model_validate(research_request)
    
    def get_research_requests(self, offset: int = 0, limit: int = 10, 
                            status: str = None) -> List[ResearchRequestResponse]:
        """Get paginated list of research requests."""
        query = self.db.query(ResearchRequest)
        
        if status:
            query = query.filter(ResearchRequest.status == status)
        
        requests = query.order_by(ResearchRequest.created_at.desc()).offset(offset).limit(limit).all()
        
        return [ResearchRequestResponse.model_validate(req) for req in requests]
    
    def get_research_requests_count(self, status: str = None) -> int:
        """Get total count of research requests."""
        query = self.db.query(ResearchRequest)
        
        if status:
            query = query.filter(ResearchRequest.status == status)
        
        return query.count()
    
    def delete_research_request(self, request_id: int) -> bool:
        """Delete a research request and all associated data."""
        research_request = self.db.query(ResearchRequest).filter(
            ResearchRequest.id == request_id
        ).first()
        
        if not research_request:
            return False
        
        self.db.delete(research_request)
        self.db.commit()
        
        return True
    
    # Workflow log methods
    def create_workflow_log(self, request_id: int, step: WorkflowStep, 
                          status: str, message: str = None, details: dict = None) -> WorkflowLogResponse:
        """Create a workflow log entry."""
        log = WorkflowLog(
            research_request_id=request_id,
            step=step,
            status=status,
            message=message,
            details=details
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return WorkflowLogResponse.model_validate(log)
    
    def update_workflow_log(self, log_id: int, status: str, message: str = None, 
                          details: dict = None) -> Optional[WorkflowLogResponse]:
        """Update a workflow log entry."""
        log = self.db.query(WorkflowLog).filter(WorkflowLog.id == log_id).first()
        
        if not log:
            return None
        
        log.status = status
        if message:
            log.message = message
        if details:
            log.details = details
        if status == "completed":
            log.completed_at = datetime.utcnow()
            if log.started_at:
                duration = (log.completed_at - log.started_at).total_seconds() * 1000
                log.duration_ms = int(duration)
        
        self.db.commit()
        self.db.refresh(log)
        
        return WorkflowLogResponse.model_validate(log)
    
    def get_workflow_logs(self, request_id: int) -> List[WorkflowLogResponse]:
        """Get all workflow logs for a research request."""
        logs = self.db.query(WorkflowLog).filter(
            WorkflowLog.research_request_id == request_id
        ).order_by(WorkflowLog.started_at).all()
        
        return [WorkflowLogResponse.model_validate(log) for log in logs]
    
    # Article methods
    def create_article(self, request_id: int, title: str, url: str, source: str,
                      content: str = None, summary: str = None, keywords: List[str] = None,
                      published_at: datetime = None, relevance_score: int = 0) -> ArticleResponse:
        """Create an article entry."""
        article = Article(
            research_request_id=request_id,
            title=title,
            url=url,
            source=source,
            content=content,
            summary=summary,
            keywords=keywords,
            published_at=published_at,
            relevance_score=relevance_score
        )
        
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        
        return ArticleResponse.model_validate(article)
    
    def get_articles(self, request_id: int, limit: int = None) -> List[ArticleResponse]:
        """Get articles for a research request."""
        query = self.db.query(Article).filter(
            Article.research_request_id == request_id
        ).order_by(Article.relevance_score.desc(), Article.extracted_at)
        
        if limit:
            query = query.limit(limit)
        
        articles = query.all()
        
        return [ArticleResponse.model_validate(article) for article in articles]