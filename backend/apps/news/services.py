import logging
from datetime import datetime
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import NewsSource, NewsArticle, StockMention, NewsCategory, ArticleCategory
from .ml_utils import MLUtils
from .validators import NewsDataValidator

logger = logging.getLogger(__name__)

class NewsIngestionService:
    """Service for ingesting and processing news articles"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.ml_utils = MLUtils()

    def fetch_article(self, url: str) -> Dict[str, Any]:
        """Fetch article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article content (customize based on source)
            title = soup.find('h1').text.strip() if soup.find('h1') else ''
            content = ' '.join([p.text.strip() for p in soup.find_all('p')])
            author = soup.find('meta', {'name': 'author'})
            author = author['content'] if author else ''
            
            # Clean and validate data
            data = {
                'title': title,
                'content': content,
                'author': author,
                'url': url
            }
            return NewsDataValidator.validate_article_data(data)
            
        except Exception as e:
            logger.error(f"Error fetching article from {url}: {str(e)}")
            raise

    def extract_stock_mentions(self, content: str) -> List[str]:
        """Extract stock symbols from content"""
        return NewsDataValidator.extract_stock_mentions(content)

    @transaction.atomic
    def process_article(self, source: NewsSource, article_data: Dict[str, Any]) -> NewsArticle:
        """Process and save article"""
        try:
            # Create or update article
            article, created = NewsArticle.objects.update_or_create(
                url=article_data['url'],
                defaults={
                    'title': article_data['title'],
                    'content': article_data['content'],
                    'source': source,
                    'author': article_data.get('author', ''),
                    'published_at': article_data.get('published_at', timezone.now())
                }
            )

            # Extract and save stock mentions
            stock_symbols = self.extract_stock_mentions(article_data['content'])
            for symbol in stock_symbols:
                StockMention.objects.get_or_create(
                    article=article,
                    symbol=symbol,
                    defaults={'context': ''}
                )

            return article

        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            raise

    def ingest_from_source(self, source: NewsSource) -> List[NewsArticle]:
        """Ingest articles from a news source"""
        articles = []
        try:
            # Fetch articles from source
            # This is a placeholder - implement actual fetching logic
            article_urls = self._get_article_urls(source)
            
            for url in article_urls:
                try:
                    article_data = self.fetch_article(url)
                    article = self.process_article(source, article_data)
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing article {url}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error ingesting from source {source.name}: {str(e)}")
            raise

        return articles

    def _get_article_urls(self, source: NewsSource) -> List[str]:
        """Get article URLs from source"""
        # Implement source-specific URL extraction
        # This is a placeholder - you'll need to implement the actual logic
        return []

class NewsProcessingService:
    """Service for processing and analyzing news articles"""

    def __init__(self):
        self.ml_utils = MLUtils()

    def generate_summary(self, article: NewsArticle) -> str:
        """Generate article summary"""
        return self.ml_utils.generate_summary(article.content)

    def analyze_sentiment(self, text: str) -> float:
        """Analyze text sentiment"""
        return self.ml_utils.analyze_sentiment(text)

    def categorize_article(self, article: NewsArticle) -> List[Dict[str, float]]:
        """Categorize article"""
        return self.ml_utils.categorize_article(article.content)

    @transaction.atomic
    def process_article(self, article: NewsArticle) -> None:
        """Process article with all analysis steps"""
        try:
            # Generate summary
            article.summary = self.generate_summary(article)
            
            # Analyze sentiment
            article.sentiment_score = self.analyze_sentiment(article.content)
            
            # Generate embedding
            article.embedding_vector = self.ml_utils.generate_embedding(article.content)
            
            # Categorize article
            categories = self.categorize_article(article)
            for category_data in categories:
                category, created = NewsCategory.objects.get_or_create(
                    name=category_data['name']
                )
                ArticleCategory.objects.get_or_create(
                    article=article,
                    category=category,
                    defaults={'confidence_score': category_data['confidence']}
                )
            
            # Update stock mentions with sentiment
            for mention in article.stock_mentions.all():
                mention.sentiment_score = self.analyze_sentiment(mention.context)
                mention.save()
            
            article.is_processed = True
            article.save()

        except Exception as e:
            logger.error(f"Error processing article {article.id}: {str(e)}")
            raise 