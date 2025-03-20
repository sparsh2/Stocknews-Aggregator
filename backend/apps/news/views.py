from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from .models import NewsSource, NewsArticle, StockMention, NewsCategory, ArticleCategory
from .serializers import (
    NewsSourceSerializer, NewsArticleSerializer, NewsArticleCreateSerializer,
    NewsArticleUpdateSerializer, StockMentionSerializer, StockMentionCreateSerializer,
    NewsCategorySerializer, ArticleCategorySerializer, ArticleCategoryCreateSerializer
)
from .services import NewsProcessingService
from apps.api.throttling import NewsIngestionThrottle, ArticleProcessingThrottle
from apps.api.decorators import cache_response, invalidate_cache

class NewsSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing news sources"""
    queryset = NewsSource.objects.all()
    serializer_class = NewsSourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    throttle_classes = [NewsIngestionThrottle]

    @cache_response(timeout=settings.CACHE_TIMEOUT_LONG)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=settings.CACHE_TIMEOUT_LONG)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache('GET:news/sources/*')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache('GET:news/sources/*')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache('GET:news/sources/*')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def ingest_articles(self, request, pk=None):
        """Trigger article ingestion for a source"""
        source = self.get_object()
        try:
            from .tasks import ingest_news_from_source
            task = ingest_news_from_source.delay(source.id)
            return Response({
                'status': 'success',
                'message': 'Article ingestion started',
                'task_id': task.id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NewsArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing news articles"""
    queryset = NewsArticle.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'is_processed']
    search_fields = ['title', 'content', 'author']
    ordering_fields = ['published_at', 'created_at', 'sentiment_score']
    ordering = ['-published_at']
    throttle_classes = [ArticleProcessingThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NewsArticleUpdateSerializer
        return NewsArticleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by stock symbol
        symbol = self.request.query_params.get('symbol', None)
        if symbol:
            queryset = queryset.filter(stock_mentions__symbol=symbol)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__category__name=category)
        
        # Filter by sentiment range
        min_sentiment = self.request.query_params.get('min_sentiment', None)
        max_sentiment = self.request.query_params.get('max_sentiment', None)
        if min_sentiment is not None:
            queryset = queryset.filter(sentiment_score__gte=float(min_sentiment))
        if max_sentiment is not None:
            queryset = queryset.filter(sentiment_score__lte=float(max_sentiment))
        
        return queryset.distinct()

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache('GET:news/articles/*')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache('GET:news/articles/*')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache('GET:news/articles/*')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def process_article(self, request, pk=None):
        """Trigger article processing"""
        article = self.get_object()
        try:
            from .tasks import process_article
            task = process_article.delay(article.id)
            return Response({
                'status': 'success',
                'message': 'Article processing started',
                'task_id': task.id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def similar_articles(self, request):
        """Find similar articles using semantic search"""
        article_id = request.query_params.get('article_id', None)
        if not article_id:
            return Response({
                'status': 'error',
                'message': 'article_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            article = NewsArticle.objects.get(id=article_id)
            if not article.embedding_vector:
                return Response({
                    'status': 'error',
                    'message': 'Article has not been processed yet'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use Milvus for similarity search
            from .ml_utils import MLUtils
            ml_utils = MLUtils()
            similar_articles = ml_utils.vector_store.similarity_search(
                article.embedding_vector,
                k=5
            )
            
            serializer = self.get_serializer(similar_articles, many=True)
            return Response(serializer.data)
            
        except NewsArticle.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Article not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StockMentionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock mentions"""
    queryset = StockMention.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['article']
    search_fields = ['symbol']
    ordering_fields = ['created_at', 'sentiment_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StockMentionCreateSerializer
        return StockMentionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by sentiment range
        min_sentiment = self.request.query_params.get('min_sentiment', None)
        max_sentiment = self.request.query_params.get('max_sentiment', None)
        if min_sentiment is not None:
            queryset = queryset.filter(sentiment_score__gte=float(min_sentiment))
        if max_sentiment is not None:
            queryset = queryset.filter(sentiment_score__lte=float(max_sentiment))
        
        return queryset

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache('GET:news/stock-mentions/*')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache('GET:news/stock-mentions/*')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache('GET:news/stock-mentions/*')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class NewsCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing news categories"""
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']

    @cache_response(timeout=settings.CACHE_TIMEOUT_LONG)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=settings.CACHE_TIMEOUT_LONG)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache('GET:news/categories/*')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache('GET:news/categories/*')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache('GET:news/categories/*')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class ArticleCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing article-category relationships"""
    queryset = ArticleCategory.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['article', 'category']
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-confidence_score']

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCategoryCreateSerializer
        return ArticleCategorySerializer

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=settings.CACHE_TIMEOUT)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache('GET:news/article-categories/*')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache('GET:news/article-categories/*')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache('GET:news/article-categories/*')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs) 