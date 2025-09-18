"""
External API services for data gathering.
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings

class WikipediaService:
    """Service for fetching data from Wikipedia API."""
    
    def __init__(self):
        self.base_url = settings.WIKIPEDIA_API_URL
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def search_articles(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for articles related to the topic."""
        try:
            # Search for articles
            search_url = f"{self.base_url}/page/search/{topic}"
            params = {
                "limit": limit,
                "suggestion": "true"
            }
            
            response = await self.session.get(search_url, params=params)
            response.raise_for_status()
            
            search_data = response.json()
            articles = []
            
            # Get detailed info for each article
            for page in search_data.get("pages", [])[:5]:  # Limit to top 5
                try:
                    article_data = await self._get_article_details(page["key"])
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.warning(f"Failed to get details for {page['key']}: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []
    
    async def _get_article_details(self, page_key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific article."""
        try:
            # Get page summary
            summary_url = f"{self.base_url}/page/summary/{page_key}"
            response = await self.session.get(summary_url)
            response.raise_for_status()
            
            summary_data = response.json()
            
            # Get page content
            content_url = f"{self.base_url}/page/html/{page_key}"
            content_response = await self.session.get(content_url)
            content_response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(content_response.text, 'html.parser')
            
            # Extract text content (first few paragraphs)
            paragraphs = soup.find_all('p')
            content_text = ' '.join([p.get_text().strip() for p in paragraphs[:3] if p.get_text().strip()])
            
            return {
                "title": summary_data.get("title", ""),
                "url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "summary": summary_data.get("extract", ""),
                "content": content_text[:2000],  # Limit content length
                "source": "wikipedia",
                "published_at": None,
                "relevance_score": 80  # Wikipedia articles are generally high quality
            }
            
        except Exception as e:
            logger.error(f"Failed to get Wikipedia article details: {e}")
            return None
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()

class HackerNewsService:
    """Service for fetching data from Hacker News API."""
    
    def __init__(self):
        self.base_url = settings.HACKERNEWS_API_URL
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def search_stories(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for stories related to the topic."""
        try:
            # Get top stories
            top_stories_url = f"{self.base_url}/topstories.json"
            response = await self.session.get(top_stories_url)
            response.raise_for_status()
            
            story_ids = response.json()[:100]  # Get top 100 stories
            
            # Search through stories for relevant ones
            relevant_stories = []
            search_terms = topic.lower().split()
            
            # Process stories in batches
            for i in range(0, min(len(story_ids), 50), 10):  # Check first 50 stories in batches of 10
                batch_ids = story_ids[i:i+10]
                batch_stories = await self._get_stories_batch(batch_ids)
                
                for story in batch_stories:
                    if story and self._is_relevant(story, search_terms):
                        relevant_stories.append(story)
                        if len(relevant_stories) >= limit:
                            break
                
                if len(relevant_stories) >= limit:
                    break
            
            return relevant_stories[:limit]
            
        except Exception as e:
            logger.error(f"HackerNews search failed: {e}")
            return []
    
    async def _get_stories_batch(self, story_ids: List[int]) -> List[Optional[Dict[str, Any]]]:
        """Get a batch of stories concurrently."""
        tasks = [self._get_story_details(story_id) for story_id in story_ids]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _get_story_details(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific story."""
        try:
            story_url = f"{self.base_url}/item/{story_id}.json"
            response = await self.session.get(story_url)
            response.raise_for_status()
            
            story_data = response.json()
            
            if story_data.get("type") != "story" or story_data.get("deleted"):
                return None
            
            return {
                "title": story_data.get("title", ""),
                "url": story_data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                "summary": story_data.get("text", "")[:500] if story_data.get("text") else "",
                "content": story_data.get("text", ""),
                "source": "hackernews",
                "published_at": datetime.fromtimestamp(story_data.get("time", 0)) if story_data.get("time") else None,
                "relevance_score": min(story_data.get("score", 0), 100)  # Use HN score as relevance
            }
            
        except Exception as e:
            logger.error(f"Failed to get HackerNews story details: {e}")
            return None
    
    def _is_relevant(self, story: Dict[str, Any], search_terms: List[str]) -> bool:
        """Check if a story is relevant to the search terms."""
        if not story:
            return False
        
        title = story.get("title", "").lower()
        text = story.get("content", "").lower()
        
        # Check if any search term appears in title or content
        for term in search_terms:
            if term in title or term in text:
                return True
        
        return False
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()

class ContentProcessor:
    """Service for processing and analyzing content."""
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using simple frequency analysis."""
        if not text:
            return []
        
        # Clean and tokenize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    @staticmethod
    def generate_summary(text: str, max_sentences: int = 3) -> str:
        """Generate a simple extractive summary."""
        if not text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
        
        # For simplicity, take the first few sentences
        # In a real implementation, you might use more sophisticated summarization
        summary_sentences = sentences[:max_sentences]
        return '. '.join(summary_sentences) + '.'

class ExternalAPIService:
    """Main service for coordinating external API calls."""
    
    def __init__(self):
        self.wikipedia = WikipediaService()
        self.hackernews = HackerNewsService()
        self.processor = ContentProcessor()
    
    async def gather_research_data(self, topic: str) -> List[Dict[str, Any]]:
        """Gather research data from all external sources."""
        logger.info(f"Gathering research data for topic: {topic}")
        
        try:
            # Fetch data from multiple sources concurrently
            wikipedia_task = self.wikipedia.search_articles(topic, limit=3)
            hackernews_task = self.hackernews.search_stories(topic, limit=2)
            
            wikipedia_articles, hackernews_stories = await asyncio.gather(
                wikipedia_task, hackernews_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(wikipedia_articles, Exception):
                logger.error(f"Wikipedia fetch failed: {wikipedia_articles}")
                wikipedia_articles = []
            
            if isinstance(hackernews_stories, Exception):
                logger.error(f"HackerNews fetch failed: {hackernews_stories}")
                hackernews_stories = []
            
            # Combine all articles
            all_articles = []
            all_articles.extend(wikipedia_articles or [])
            all_articles.extend(hackernews_stories or [])
            
            # Process articles
            processed_articles = []
            for article in all_articles:
                if article:
                    # Generate summary if not present
                    if not article.get("summary") and article.get("content"):
                        article["summary"] = self.processor.generate_summary(article["content"])
                    
                    # Extract keywords
                    text_for_keywords = f"{article.get('title', '')} {article.get('content', '')}"
                    article["keywords"] = self.processor.extract_keywords(text_for_keywords)
                    
                    processed_articles.append(article)
            
            # Sort by relevance score
            processed_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            logger.info(f"Gathered {len(processed_articles)} articles for topic: {topic}")
            return processed_articles[:5]  # Return top 5 articles
            
        except Exception as e:
            logger.error(f"Failed to gather research data: {e}")
            return []
    
    async def close(self):
        """Close all HTTP sessions."""
        await self.wikipedia.close()
        await self.hackernews.close()