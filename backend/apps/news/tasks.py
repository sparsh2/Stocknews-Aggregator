import logging
from celery import shared_task
from django.utils import timezone
from .models import NewsSource, NewsArticle
from .services import NewsIngestionService, NewsProcessingService

logger = logging.getLogger(__name__)

@shared_task
def ingest_news_from_sources():
    """Task to ingest news from all active sources"""
    try:
        ingestion_service = NewsIngestionService()
        processing_service = NewsProcessingService()
        
        # Get all active sources
        sources = NewsSource.objects.filter(is_active=True)
        
        for source in sources:
            try:
                # Ingest articles from source
                articles = ingestion_service.ingest_from_source(source)
                
                # Process each article
                for article in articles:
                    process_article.delay(article.id)
                    
            except Exception as e:
                logger.error(f"Error processing source {source.name}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in ingest_news_from_sources task: {str(e)}")
        raise

@shared_task
def process_article(article_id: int):
    """Task to process a single article"""
    try:
        article = NewsArticle.objects.get(id=article_id)
        processing_service = NewsProcessingService()
        processing_service.process_article(article)
    except NewsArticle.DoesNotExist:
        logger.error(f"Article with id {article_id} not found")
    except Exception as e:
        logger.error(f"Error processing article {article_id}: {str(e)}")
        raise

@shared_task
def cleanup_old_articles(days: int = 30):
    """Task to clean up old articles"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count = NewsArticle.objects.filter(
            published_at__lt=cutoff_date
        ).delete()[0]
        logger.info(f"Deleted {deleted_count} old articles")
    except Exception as e:
        logger.error(f"Error in cleanup_old_articles task: {str(e)}")
        raise

@shared_task
def reprocess_failed_articles():
    """Task to reprocess articles that failed processing"""
    try:
        failed_articles = NewsArticle.objects.filter(
            is_processed=False
        ).order_by('-created_at')[:100]  # Process 100 at a time
        
        for article in failed_articles:
            process_article.delay(article.id)
            
    except Exception as e:
        logger.error(f"Error in reprocess_failed_articles task: {str(e)}")
        raise 