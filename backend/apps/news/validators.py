import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)

class NewsDataValidator:
    """Validator for news data"""

    # Common stock symbol patterns
    STOCK_SYMBOL_PATTERN = r'\$[A-Z]{1,5}|[A-Z]{1,5}'
    
    # Common date formats
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%B %d, %Y',
        '%B %d %Y',
        '%d %B %Y',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()

    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate and clean URL"""
        if not url:
            raise ValidationError('URL is required')
            
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
        if not url_pattern.match(url):
            raise ValidationError('Invalid URL format')
            
        return url

    @classmethod
    def validate_date(cls, date_str: str) -> datetime:
        """Validate and parse date string"""
        if not date_str:
            return timezone.now()
            
        for fmt in cls.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        raise ValidationError(f'Invalid date format. Supported formats: {", ".join(cls.DATE_FORMATS)}')

    @classmethod
    def validate_stock_symbol(cls, symbol: str) -> str:
        """Validate and clean stock symbol"""
        if not symbol:
            raise ValidationError('Stock symbol is required')
            
        # Remove common prefixes and clean
        symbol = symbol.replace('$', '').strip().upper()
        
        # Validate format
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            raise ValidationError('Invalid stock symbol format')
            
        return symbol

    @classmethod
    def validate_article_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean article data"""
        cleaned_data = {}
        
        try:
            # Required fields
            cleaned_data['title'] = cls.clean_text(data.get('title', ''))
            if not cleaned_data['title']:
                raise ValidationError('Article title is required')
                
            cleaned_data['content'] = cls.clean_text(data.get('content', ''))
            if not cleaned_data['content']:
                raise ValidationError('Article content is required')
                
            cleaned_data['url'] = cls.validate_url(data.get('url', ''))
            
            # Optional fields
            cleaned_data['author'] = cls.clean_text(data.get('author', ''))
            cleaned_data['published_at'] = cls.validate_date(data.get('published_at', ''))
            
            # Validate length constraints
            if len(cleaned_data['title']) > 500:
                raise ValidationError('Title exceeds maximum length of 500 characters')
                
            if len(cleaned_data['content']) < 100:
                raise ValidationError('Content must be at least 100 characters long')
                
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating article data: {str(e)}")
            raise ValidationError(f"Invalid article data: {str(e)}")

    @classmethod
    def validate_source_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean news source data"""
        cleaned_data = {}
        
        try:
            # Required fields
            cleaned_data['name'] = cls.clean_text(data.get('name', ''))
            if not cleaned_data['name']:
                raise ValidationError('Source name is required')
                
            cleaned_data['url'] = cls.validate_url(data.get('url', ''))
            
            # Optional fields
            cleaned_data['description'] = cls.clean_text(data.get('description', ''))
            cleaned_data['active'] = bool(data.get('active', True))
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating source data: {str(e)}")
            raise ValidationError(f"Invalid source data: {str(e)}")

    @classmethod
    def validate_category_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean category data"""
        cleaned_data = {}
        
        try:
            # Required fields
            cleaned_data['name'] = cls.clean_text(data.get('name', ''))
            if not cleaned_data['name']:
                raise ValidationError('Category name is required')
                
            # Optional fields
            cleaned_data['description'] = cls.clean_text(data.get('description', ''))
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating category data: {str(e)}")
            raise ValidationError(f"Invalid category data: {str(e)}")

    @classmethod
    def extract_stock_mentions(cls, text: str) -> List[str]:
        """Extract and validate stock symbols from text"""
        if not text:
            return []
            
        # Find all potential stock symbols
        matches = re.finditer(cls.STOCK_SYMBOL_PATTERN, text)
        symbols = set()
        
        for match in matches:
            try:
                symbol = cls.validate_stock_symbol(match.group())
                symbols.add(symbol)
            except ValidationError:
                continue
                
        return list(symbols) 