"""
Complete Ottawa.ca Web Scraper
Based on your successful Scrapy implementation
"""

import scrapy
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class OttawaSpider(scrapy.Spider):
    """
    Complete spider for scraping Ottawa city services
    This is your production-ready scraper that collected 133 documents
    """
    
    name = 'ottawa_complete'
    allowed_domains = ['ottawa.ca']
    
    # Comprehensive starting URLs
    start_urls = [
        'https://ottawa.ca/en',
        'https://ottawa.ca/en/city-hall',
        'https://ottawa.ca/en/residents',
        'https://ottawa.ca/en/business',
        'https://ottawa.ca/en/recreation-and-culture',
        'https://ottawa.ca/en/planning-development-and-construction',
        'https://ottawa.ca/en/health-and-public-safety',
        'https://ottawa.ca/en/garbage-and-recycling',
        'https://ottawa.ca/en/parking',
        'https://ottawa.ca/en/transportation',
    ]
    
    def __init__(self, max_pages=200, output_dir="data/raw", *args, **kwargs):
        super(OttawaSpider, self).__init__(*args, **kwargs)
        self.max_pages = max_pages
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scraped_count = 0
        
    def parse(self, response):
        """Main parsing method - extracts content and follows links"""
        
        if self.scraped_count >= self.max_pages:
            return
        
        # Extract main content
        content = self.extract_main_content(response)
        
        if content and len(content) > 200:  # Only save substantial content
            self.save_page_content(response.url, content, response)
            self.scraped_count += 1
            
            # Continue crawling if under limit
            if self.scraped_count < self.max_pages:
                # Follow internal links
                for link in response.css('a::attr(href)').getall():
                    full_url = urljoin(response.url, link)
                    
                    if (self.is_valid_ottawa_url(full_url) and 
                        not self.is_unwanted_file(full_url)):
                        yield response.follow(link, self.parse)
    
    def extract_main_content(self, response) -> str:
        """Extract clean text content from Ottawa pages"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                               'aside', 'iframe', 'noscript', 'form']):
                element.decompose()
            
            # Try to find main content areas (Ottawa.ca specific)
            main_selectors = [
                'main',
                '.content',
                'article',
                '#content',
                '.main-content',
                '.page-content'
            ]
            
            main_content = None
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    text = body.get_text(separator=' ', strip=True)
                else:
                    text = soup.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)  # Multiple whitespace to single
            text = text.strip()
            
            return text if len(text) > 200 else None
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {response.url}: {e}")
            return None
    
    def save_page_content(self, url: str, content: str, response):
        """Save page content as JSON with metadata"""
        try:
            filename = self.url_to_filename(url)
            filepath = self.output_dir / f"{filename}.json"
            
            # Extract additional metadata
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ""
            
            data = {
                'url': url,
                'title': title_text,
                'description': description,
                'content': content,
                'content_length': len(content),
                'timestamp': response.headers.get('Date', '').decode('utf-8', errors='ignore'),
                'scraped_at': scrapy.utils.misc.load_object('datetime').datetime.now().isoformat(),
                'source_file': f"{filename}.json"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved: {filename}.json ({len(content)} chars)")
            
        except Exception as e:
            self.logger.error(f"Error saving {url}: {e}")
    
    def url_to_filename(self, url: str) -> str:
        """Convert URL to safe filename"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Clean up path
        filename = re.sub(r'[^\w\-_/]', '_', path)
        filename = filename.strip('_/').replace('/', '_')
        
        # Limit length and ensure uniqueness
        if len(filename) > 100:
            filename = filename[:100]
        
        if not filename:
            filename = f"page_{self.scraped_count}"
        
        return filename
    
    def is_valid_ottawa_url(self, url: str) -> bool:
        """Check if URL should be scraped"""
        try:
            parsed = urlparse(url)
            
            # Must be ottawa.ca
            if 'ottawa.ca' not in parsed.netloc:
                return False
            
            # Skip unwanted paths
            unwanted_paths = [
                '/calendar/', '/events/', '/archive/', '/search/',
                '/contact/', '/feedback/', '/subscribe/', '/fr/',
                '/api/', '/admin/', '/login/', '/logout/'
            ]
            
            for unwanted in unwanted_paths:
                if unwanted in parsed.path:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def is_unwanted_file(self, url: str) -> bool:
        """Check for unwanted file types"""
        unwanted_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js',
            '.zip', '.rar', '.exe', '.mp4', '.mp3', '.wav'
        ]
        
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in unwanted_extensions)