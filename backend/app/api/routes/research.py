"""
Research API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import math

from app.core.database import get_db
from app.schemas.research import (
    ResearchRequestCreate,
    ResearchRequestResponse,
    ResearchRequestDetailResponse,
    ResearchRequestListResponse,
    WorkflowLogResponse
)
from app.services.research import ResearchService
from app.tasks.research_workflow import start_research_workflow

router = APIRouter()

@router.post("/research", response_model=ResearchRequestResponse)
async def create_research_request(
    request: ResearchRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new research topic for processing.
    
    This endpoint:
    1. Validates the input topic
    2. Creates a research request in the database
    3. Starts the background research workflow
    4. Returns the request details with task ID
    """
    try:
        # Create research service
        research_service = ResearchService(db)
        
        # Create research request
        research_request = research_service.create_research_request(request.topic)
        
        # Start background workflow
        task = start_research_workflow.delay(research_request.id)
        
        # Update with task ID
        research_request = research_service.update_task_id(research_request.id, task.id)
        
        return research_request
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create research request: {str(e)}")

@router.get("/research", response_model=ResearchRequestListResponse)
async def list_research_requests(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    List all research requests with pagination and filtering.
    
    Returns a paginated list of research requests with optional status filtering.
    """
    try:
        research_service = ResearchService(db)
        
        # Get total count
        total = research_service.get_research_requests_count(status)
        
        # Calculate pagination
        offset = (page - 1) * size
        pages = math.ceil(total / size)
        
        # Get requests
        requests = research_service.get_research_requests(
            offset=offset,
            limit=size,
            status=status
        )
        
        return ResearchRequestListResponse(
            items=requests,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list research requests: {str(e)}")

@router.get("/research/{request_id}", response_model=ResearchRequestDetailResponse)
async def get_research_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific research request.
    
    Returns the research request with all logs and articles.
    """
    try:
        research_service = ResearchService(db)
        
        # Get research request
        research_request = research_service.get_research_request_detail(request_id)
        
        if not research_request:
            raise HTTPException(status_code=404, detail="Research request not found")
        
        return research_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research request: {str(e)}")

@router.get("/research/{request_id}/logs", response_model=List[WorkflowLogResponse])
async def get_research_logs(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Get workflow logs for a specific research request.
    
    Returns all workflow execution logs in chronological order.
    """
    try:
        research_service = ResearchService(db)
        
        # Check if request exists
        research_request = research_service.get_research_request(request_id)
        if not research_request:
            raise HTTPException(status_code=404, detail="Research request not found")
        
        # Get logs
        logs = research_service.get_workflow_logs(request_id)
        
        return logs
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research logs: {str(e)}")

@router.delete("/research/{request_id}")
async def delete_research_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a research request and all associated data.
    
    This will remove the request, logs, and articles from the database.
    """
    try:
        research_service = ResearchService(db)
        
        # Check if request exists
        research_request = research_service.get_research_request(request_id)
        if not research_request:
            raise HTTPException(status_code=404, detail="Research request not found")
        
        # Delete request
        research_service.delete_research_request(request_id)
        
        return {"message": "Research request deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete research request: {str(e)}")