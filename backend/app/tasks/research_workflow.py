"""
Celery tasks for research workflow execution.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from app.celery import celery_app
from app.core.database import SessionLocal
from app.services.research import ResearchService
from app.services.external_apis import ExternalAPIService
from app.models.research import ResearchStatus, WorkflowStep

@celery_app.task(bind=True)
def start_research_workflow(self, request_id: int):
    """
    Main research workflow task.
    
    Executes the 5-step research process:
    1. Input Parsing
    2. Data Gathering
    3. Processing
    4. Result Persistence
    5. Return Results
    """
    db = SessionLocal()
    research_service = ResearchService(db)
    
    try:
        logger.info(f"Starting research workflow for request {request_id}")
        
        # Get research request
        research_request = research_service.get_research_request(request_id)
        if not research_request:
            raise Exception(f"Research request {request_id} not found")
        
        # Update status to processing
        research_service.update_status(request_id, ResearchStatus.PROCESSING)
        
        # Execute workflow steps
        workflow_start = datetime.utcnow()
        
        # Step 1: Input Parsing
        step1_result = execute_input_parsing(research_service, request_id, research_request.topic)
        
        # Step 2: Data Gathering
        step2_result = execute_data_gathering(research_service, request_id, research_request.topic)
        
        # Step 3: Processing
        step3_result = execute_processing(research_service, request_id, step2_result)
        
        # Step 4: Result Persistence
        step4_result = execute_result_persistence(research_service, request_id, step3_result)
        
        # Step 5: Return Results
        final_results = execute_return_results(research_service, request_id, step4_result, workflow_start)
        
        # Update status to completed
        research_service.update_status(
            request_id, 
            ResearchStatus.COMPLETED, 
            results=final_results
        )
        
        logger.info(f"Research workflow completed for request {request_id}")
        return final_results
        
    except Exception as e:
        logger.error(f"Research workflow failed for request {request_id}: {e}")
        
        # Log error
        research_service.create_workflow_log(
            request_id,
            WorkflowStep.RETURN_RESULTS,
            "failed",
            f"Workflow failed: {str(e)}"
        )
        
        # Update status to failed
        research_service.update_status(
            request_id,
            ResearchStatus.FAILED,
            error_message=str(e)
        )
        
        raise
    
    finally:
        db.close()

def execute_input_parsing(research_service: ResearchService, request_id: int, topic: str) -> Dict[str, Any]:
    """Step 1: Input Parsing and Validation."""
    logger.info(f"Step 1: Input parsing for request {request_id}")
    
    # Create log entry
    log = research_service.create_workflow_log(
        request_id,
        WorkflowStep.INPUT_PARSING,
        "started",
        "Validating and parsing input topic"
    )
    
    try:
        # Validate topic
        if not topic or len(topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        
        if len(topic) > 500:
            raise ValueError("Topic must be less than 500 characters")
        
        # Parse and clean topic
        cleaned_topic = topic.strip()
        
        result = {
            "original_topic": topic,
            "cleaned_topic": cleaned_topic,
            "topic_length": len(cleaned_topic),
            "validation_passed": True
        }
        
        # Update log
        research_service.update_workflow_log(
            log.id,
            "completed",
            "Input validation completed successfully",
            result
        )
        
        logger.info(f"Step 1 completed for request {request_id}")
        return result
        
    except Exception as e:
        research_service.update_workflow_log(
            log.id,
            "failed",
            f"Input validation failed: {str(e)}"
        )
        raise

def execute_data_gathering(research_service: ResearchService, request_id: int, topic: str) -> List[Dict[str, Any]]:
    """Step 2: Data Gathering from External APIs."""
    logger.info(f"Step 2: Data gathering for request {request_id}")
    
    # Create log entry
    log = research_service.create_workflow_log(
        request_id,
        WorkflowStep.DATA_GATHERING,
        "started",
        "Fetching articles from external APIs"
    )
    
    try:
        # Initialize external API service
        api_service = ExternalAPIService()
        
        # Gather data asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            articles = loop.run_until_complete(api_service.gather_research_data(topic))
        finally:
            loop.run_until_complete(api_service.close())
            loop.close()
        
        # Update log
        research_service.update_workflow_log(
            log.id,
            "completed",
            f"Successfully gathered {len(articles)} articles",
            {
                "articles_count": len(articles),
                "sources": list(set(article.get("source", "unknown") for article in articles))
            }
        )
        
        logger.info(f"Step 2 completed for request {request_id}: {len(articles)} articles gathered")
        return articles
        
    except Exception as e:
        research_service.update_workflow_log(
            log.id,
            "failed",
            f"Data gathering failed: {str(e)}"
        )
        raise

def execute_processing(research_service: ResearchService, request_id: int, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Step 3: Processing - Extract top 5 articles, summarize, and extract keywords."""
    logger.info(f"Step 3: Processing for request {request_id}")
    
    # Create log entry
    log = research_service.create_workflow_log(
        request_id,
        WorkflowStep.PROCESSING,
        "started",
        "Processing articles and extracting insights"
    )
    
    try:
        # Select top 5 articles
        top_articles = articles[:5]
        
        # Extract all keywords
        all_keywords = []
        for article in top_articles:
            keywords = article.get("keywords", [])
            all_keywords.extend(keywords)
        
        # Get unique keywords and sort by frequency
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_keywords = [keyword for keyword, freq in top_keywords]
        
        # Generate overall summary
        all_summaries = [article.get("summary", "") for article in top_articles if article.get("summary")]
        overall_summary = " ".join(all_summaries)[:1000]  # Limit to 1000 chars
        
        # Get sources
        sources = list(set(article.get("source", "unknown") for article in top_articles))
        
        result = {
            "top_articles": top_articles,
            "keywords": top_keywords,
            "summary": overall_summary,
            "sources": sources,
            "total_articles_processed": len(articles),
            "top_articles_count": len(top_articles)
        }
        
        # Update log
        research_service.update_workflow_log(
            log.id,
            "completed",
            f"Processing completed: {len(top_articles)} articles processed",
            {
                "keywords_extracted": len(top_keywords),
                "summary_length": len(overall_summary),
                "sources": sources
            }
        )
        
        logger.info(f"Step 3 completed for request {request_id}")
        return result
        
    except Exception as e:
        research_service.update_workflow_log(
            log.id,
            "failed",
            f"Processing failed: {str(e)}"
        )
        raise

def execute_result_persistence(research_service: ResearchService, request_id: int, processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Step 4: Result Persistence - Save processed results to database."""
    logger.info(f"Step 4: Result persistence for request {request_id}")
    
    # Create log entry
    log = research_service.create_workflow_log(
        request_id,
        WorkflowStep.RESULT_PERSISTENCE,
        "started",
        "Saving processed results to database"
    )
    
    try:
        # Save articles to database
        saved_articles = []
        for article_data in processed_data.get("top_articles", []):
            article = research_service.create_article(
                request_id=request_id,
                title=article_data.get("title", ""),
                url=article_data.get("url", ""),
                source=article_data.get("source", ""),
                content=article_data.get("content", ""),
                summary=article_data.get("summary", ""),
                keywords=article_data.get("keywords", []),
                published_at=article_data.get("published_at"),
                relevance_score=article_data.get("relevance_score", 0)
            )
            saved_articles.append(article)
        
        # Prepare final results
        result = {
            "articles_saved": len(saved_articles),
            "keywords": processed_data.get("keywords", []),
            "summary": processed_data.get("summary", ""),
            "sources": processed_data.get("sources", []),
            "total_articles_found": processed_data.get("total_articles_processed", 0)
        }
        
        # Update log
        research_service.update_workflow_log(
            log.id,
            "completed",
            f"Results persisted: {len(saved_articles)} articles saved",
            result
        )
        
        logger.info(f"Step 4 completed for request {request_id}")
        return result
        
    except Exception as e:
        research_service.update_workflow_log(
            log.id,
            "failed",
            f"Result persistence failed: {str(e)}"
        )
        raise

def execute_return_results(research_service: ResearchService, request_id: int, 
                         persisted_data: Dict[str, Any], workflow_start: datetime) -> Dict[str, Any]:
    """Step 5: Return Results - Prepare final structured results."""
    logger.info(f"Step 5: Return results for request {request_id}")
    
    # Create log entry
    log = research_service.create_workflow_log(
        request_id,
        WorkflowStep.RETURN_RESULTS,
        "started",
        "Preparing final structured results"
    )
    
    try:
        # Get research request details
        research_request = research_service.get_research_request_detail(request_id)
        
        # Calculate processing time
        processing_time_ms = int((datetime.utcnow() - workflow_start).total_seconds() * 1000)
        
        # Get saved articles
        articles = research_service.get_articles(request_id, limit=5)
        
        # Prepare final results
        final_results = {
            "topic": research_request.topic,
            "summary": persisted_data.get("summary", ""),
            "top_articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "summary": article.summary,
                    "keywords": article.keywords,
                    "relevance_score": article.relevance_score
                }
                for article in articles
            ],
            "keywords": persisted_data.get("keywords", []),
            "sources": persisted_data.get("sources", []),
            "total_articles_found": persisted_data.get("total_articles_found", 0),
            "processing_time_ms": processing_time_ms,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Update log
        research_service.update_workflow_log(
            log.id,
            "completed",
            "Research workflow completed successfully",
            {
                "processing_time_ms": processing_time_ms,
                "articles_returned": len(articles),
                "keywords_count": len(persisted_data.get("keywords", []))
            }
        )
        
        logger.info(f"Step 5 completed for request {request_id}")
        return final_results
        
    except Exception as e:
        research_service.update_workflow_log(
            log.id,
            "failed",
            f"Return results failed: {str(e)}"
        )
        raise