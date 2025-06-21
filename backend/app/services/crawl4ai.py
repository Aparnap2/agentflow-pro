from typing import Any, Dict, List, Optional
import logging
import asyncio
import aiohttp
import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class CrawlRequest(BaseModel):
    """Crawl request configuration"""
    url: HttpUrl
    crawl_type: str = "basic"  # basic, deep, structured
    max_pages: int = 1
    follow_links: bool = False
    extract_images: bool = False
    extract_links: bool = True
    extract_text: bool = True
    extract_metadata: bool = True
    custom_selectors: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30

class CrawlResult(BaseModel):
    """Crawl result data"""
    crawl_id: str
    url: str
    status: str
    title: Optional[str] = None
    text_content: Optional[str] = None
    html_content: Optional[str] = None
    links: List[str] = []
    images: List[str] = []
    metadata: Dict[str, Any] = {}
    structured_data: Dict[str, Any] = {}
    error: Optional[str] = None
    crawled_at: str
    processing_time: float

class Crawl4AIService:
    def __init__(self):
        self.active_crawls: Dict[str, Dict[str, Any]] = {}
        self.completed_crawls: Dict[str, CrawlResult] = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def trigger_crawl(self, crawl_request: CrawlRequest) -> Dict[str, Any]:
        """Trigger a crawl job"""
        try:
            crawl_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Store crawl info
            self.active_crawls[crawl_id] = {
                'crawl_id': crawl_id,
                'url': str(crawl_request.url),
                'status': 'started',
                'started_at': start_time.isoformat(),
                'config': crawl_request.dict()
            }
            
            # Start crawling asynchronously
            asyncio.create_task(self._perform_crawl(crawl_id, crawl_request, start_time))
            
            logger.info(f"Started crawl job {crawl_id} for URL: {crawl_request.url}")
            return {
                'status': 'started',
                'crawl_id': crawl_id,
                'url': str(crawl_request.url)
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger crawl: {e}")
            return {'error': str(e)}

    async def _perform_crawl(self, crawl_id: str, crawl_request: CrawlRequest, start_time: datetime):
        """Perform the actual crawling"""
        try:
            session = await self._get_session()
            
            # Update status
            self.active_crawls[crawl_id]['status'] = 'crawling'
            
            # Prepare headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            if crawl_request.headers:
                headers.update(crawl_request.headers)
            
            # Perform the crawl
            async with session.get(str(crawl_request.url), headers=headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    result = await self._process_html(crawl_id, str(crawl_request.url), html_content, crawl_request)
                else:
                    result = CrawlResult(
                        crawl_id=crawl_id,
                        url=str(crawl_request.url),
                        status='failed',
                        error=f'HTTP {response.status}',
                        crawled_at=datetime.now().isoformat(),
                        processing_time=(datetime.now() - start_time).total_seconds()
                    )
            
            # Store result and cleanup
            self.completed_crawls[crawl_id] = result
            if crawl_id in self.active_crawls:
                del self.active_crawls[crawl_id]
            
            logger.info(f"Completed crawl job {crawl_id}")
            
        except Exception as e:
            logger.error(f"Error during crawl {crawl_id}: {e}")
            
            # Store error result
            error_result = CrawlResult(
                crawl_id=crawl_id,
                url=str(crawl_request.url),
                status='failed',
                error=str(e),
                crawled_at=datetime.now().isoformat(),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            self.completed_crawls[crawl_id] = error_result
            if crawl_id in self.active_crawls:
                del self.active_crawls[crawl_id]

    async def _process_html(self, crawl_id: str, url: str, html_content: str, crawl_request: CrawlRequest) -> CrawlResult:
        """Process HTML content and extract data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract text content
            text_content = None
            if crawl_request.extract_text:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text_content = soup.get_text()
                # Clean up text
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract links
            links = []
            if crawl_request.extract_links:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http'):
                        links.append(href)
                    elif href.startswith('/'):
                        # Convert relative URLs to absolute
                        base_url = '/'.join(url.split('/')[:3])
                        links.append(base_url + href)
            
            # Extract images
            images = []
            if crawl_request.extract_images:
                for img in soup.find_all('img', src=True):
                    src = img['src']
                    if src.startswith('http'):
                        images.append(src)
                    elif src.startswith('/'):
                        # Convert relative URLs to absolute
                        base_url = '/'.join(url.split('/')[:3])
                        images.append(base_url + src)
            
            # Extract metadata
            metadata = {}
            if crawl_request.extract_metadata:
                # Meta tags
                for meta in soup.find_all('meta'):
                    if meta.get('name'):
                        metadata[meta['name']] = meta.get('content', '')
                    elif meta.get('property'):
                        metadata[meta['property']] = meta.get('content', '')
                
                # Other useful metadata
                metadata['word_count'] = len(text_content.split()) if text_content else 0
                metadata['link_count'] = len(links)
                metadata['image_count'] = len(images)
            
            # Extract structured data using custom selectors
            structured_data = {}
            if crawl_request.custom_selectors:
                for key, selector in crawl_request.custom_selectors.items():
                    try:
                        elements = soup.select(selector)
                        structured_data[key] = [elem.get_text().strip() for elem in elements]
                    except Exception as e:
                        logger.warning(f"Failed to extract data for selector '{selector}': {e}")
                        structured_data[key] = []
            
            return CrawlResult(
                crawl_id=crawl_id,
                url=url,
                status='completed',
                title=title,
                text_content=text_content,
                html_content=html_content if crawl_request.crawl_type == 'deep' else None,
                links=links,
                images=images,
                metadata=metadata,
                structured_data=structured_data,
                crawled_at=datetime.now().isoformat(),
                processing_time=0.0  # Will be calculated by caller
            )
            
        except Exception as e:
            logger.error(f"Error processing HTML for crawl {crawl_id}: {e}")
            raise

    async def fetch_results(self, crawl_id: str) -> Dict[str, Any]:
        """Fetch crawl results"""
        try:
            # Check completed crawls first
            if crawl_id in self.completed_crawls:
                result = self.completed_crawls[crawl_id]
                return result.dict()
            
            # Check active crawls
            if crawl_id in self.active_crawls:
                return self.active_crawls[crawl_id]
            
            return {'error': f'Crawl {crawl_id} not found'}
            
        except Exception as e:
            logger.error(f"Failed to fetch results for crawl {crawl_id}: {e}")
            return {'error': str(e)}

    async def get_crawl_status(self, crawl_id: str) -> Dict[str, Any]:
        """Get crawl status"""
        try:
            if crawl_id in self.completed_crawls:
                return {
                    'crawl_id': crawl_id,
                    'status': self.completed_crawls[crawl_id].status
                }
            
            if crawl_id in self.active_crawls:
                return {
                    'crawl_id': crawl_id,
                    'status': self.active_crawls[crawl_id]['status']
                }
            
            return {'error': f'Crawl {crawl_id} not found'}
            
        except Exception as e:
            logger.error(f"Failed to get status for crawl {crawl_id}: {e}")
            return {'error': str(e)}

    async def list_crawls(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all crawls, optionally filtered by status"""
        try:
            crawls = []
            
            # Add active crawls
            for crawl_info in self.active_crawls.values():
                if status is None or crawl_info['status'] == status:
                    crawls.append(crawl_info)
            
            # Add completed crawls
            for result in self.completed_crawls.values():
                if status is None or result.status == status:
                    crawls.append({
                        'crawl_id': result.crawl_id,
                        'url': result.url,
                        'status': result.status,
                        'crawled_at': result.crawled_at
                    })
            
            return crawls
            
        except Exception as e:
            logger.error(f"Failed to list crawls: {e}")
            return []

    async def cancel_crawl(self, crawl_id: str) -> Dict[str, Any]:
        """Cancel an active crawl"""
        try:
            if crawl_id in self.active_crawls:
                # Mark as cancelled
                self.active_crawls[crawl_id]['status'] = 'cancelled'
                
                # Move to completed with cancelled status
                crawl_info = self.active_crawls[crawl_id]
                cancelled_result = CrawlResult(
                    crawl_id=crawl_id,
                    url=crawl_info['url'],
                    status='cancelled',
                    crawled_at=datetime.now().isoformat(),
                    processing_time=0.0
                )
                
                self.completed_crawls[crawl_id] = cancelled_result
                del self.active_crawls[crawl_id]
                
                logger.info(f"Cancelled crawl {crawl_id}")
                return {'status': 'cancelled', 'crawl_id': crawl_id}
            
            return {'error': f'Active crawl {crawl_id} not found'}
            
        except Exception as e:
            logger.error(f"Failed to cancel crawl {crawl_id}: {e}")
            return {'error': str(e)}

    async def cleanup_old_crawls(self, max_age_hours: int = 24):
        """Clean up old completed crawls"""
        try:
            current_time = datetime.now()
            to_remove = []
            
            for crawl_id, result in self.completed_crawls.items():
                crawled_time = datetime.fromisoformat(result.crawled_at)
                age_hours = (current_time - crawled_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    to_remove.append(crawl_id)
            
            for crawl_id in to_remove:
                del self.completed_crawls[crawl_id]
            
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} old crawl results")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old crawls: {e}")

    async def close(self):
        """Close the service and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()

    # Legacy methods for backward compatibility
    def trigger_crawl_sync(self, url: str) -> Dict[str, Any]:
        """Legacy synchronous method"""
        crawl_request = CrawlRequest(url=url)
        # This would need to be called in an async context
        return {"status": "started", "url": url, "note": "Use async trigger_crawl method"}

    def fetch_results_sync(self, crawl_id: str) -> Dict[str, Any]:
        """Legacy synchronous method"""
        if crawl_id in self.completed_crawls:
            return self.completed_crawls[crawl_id].dict()
        return {"crawl_id": crawl_id, "results": [], "note": "Use async fetch_results method"}