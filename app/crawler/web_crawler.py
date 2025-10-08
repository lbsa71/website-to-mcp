"""
Website Crawler Module
Crawls documentation sites and extracts semantic content.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebsiteCrawler:
    """Crawls website and extracts semantic content."""
    
    def __init__(self, base_url: str, max_pages: int = 100, 
                 follow_external: bool = False, timeout: int = 30,
                 delay: float = 1.0):
        self.base_url = base_url
        self.max_pages = max_pages
        self.follow_external = follow_external
        self.timeout = timeout
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.base_domain = urlparse(base_url).netloc
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled."""
        parsed = urlparse(url)
        
        # Skip non-http(s) URLs
        if parsed.scheme not in ['http', 'https']:
            return False
            
        # Skip files we don't want
        skip_extensions = ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', 
                          '.zip', '.exe', '.dmg', '.mp4', '.mp3']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        # Check domain if not following external links
        if not self.follow_external:
            return parsed.netloc == self.base_domain
            
        return True
        
    def extract_content(self, html: str, url: str) -> Dict:
        """Extract semantic content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script, style, nav, footer elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 
                        'aside', 'iframe', 'noscript']):
            tag.decompose()
            
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not main_content:
            logger.warning(f"No main content found for {url}")
            return None
            
        # Extract headers and their content
        sections = []
        current_section = {
            'title': title_text,
            'url': url,
            'headers': [],
            'paragraphs': [],
            'code_snippets': []
        }
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'code']):
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                # Start new section if we have content
                if current_section['paragraphs'] or current_section['code_snippets']:
                    sections.append(current_section)
                    current_section = {
                        'title': title_text,
                        'url': url,
                        'headers': [element.get_text().strip()],
                        'paragraphs': [],
                        'code_snippets': []
                    }
                else:
                    current_section['headers'].append(element.get_text().strip())
                    
            elif element.name == 'p':
                text = element.get_text().strip()
                if text and len(text) > 20:  # Filter out very short paragraphs
                    current_section['paragraphs'].append(text)
                    
            elif element.name in ['pre', 'code']:
                code_text = element.get_text().strip()
                if code_text and len(code_text) > 10:
                    # Avoid duplicates (pre often contains code)
                    if code_text not in current_section['code_snippets']:
                        current_section['code_snippets'].append(code_text)
        
        # Add final section
        if current_section['paragraphs'] or current_section['code_snippets']:
            sections.append(current_section)
            
        return {
            'url': url,
            'title': title_text,
            'sections': sections
        }
        
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            # Remove fragment
            url = url.split('#')[0]
            if self.is_valid_url(url) and url not in self.visited_urls:
                links.append(url)
                
        return links
        
    def crawl(self) -> List[Dict]:
        """Crawl the website starting from base_url."""
        to_visit = [self.base_url]
        all_content = []
        
        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            try:
                logger.info(f"Crawling {url} ({len(self.visited_urls) + 1}/{self.max_pages})")
                
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                self.visited_urls.add(url)
                
                # Extract content
                content = self.extract_content(response.text, url)
                if content and content['sections']:
                    all_content.append(content)
                
                # Extract and add new links
                new_links = self.extract_links(response.text, url)
                to_visit.extend(new_links)
                
                # Delay between requests
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                continue
                
        logger.info(f"Crawling complete. Visited {len(self.visited_urls)} pages.")
        return all_content


if __name__ == "__main__":
    # Test the crawler
    crawler = WebsiteCrawler("https://docs.sine.space/scripting/", max_pages=5)
    content = crawler.crawl()
    print(f"Extracted content from {len(content)} pages")
    if content:
        print(f"First page title: {content[0]['title']}")
        print(f"First page sections: {len(content[0]['sections'])}")
