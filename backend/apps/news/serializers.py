from rest_framework import serializers
from .models import NewsSource, NewsArticle, StockMention, NewsCategory, ArticleCategory

class NewsCategorySerializer(serializers.ModelSerializer):
    """Serializer for NewsCategory model"""
    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class ArticleCategorySerializer(serializers.ModelSerializer):
    """Serializer for ArticleCategory model"""
    category = NewsCategorySerializer(read_only=True)
    
    class Meta:
        model = ArticleCategory
        fields = ['id', 'category', 'confidence_score', 'created_at', 'updated_at']

class StockMentionSerializer(serializers.ModelSerializer):
    """Serializer for StockMention model"""
    class Meta:
        model = StockMention
        fields = ['id', 'symbol', 'context', 'sentiment_score', 'created_at', 'updated_at']

class NewsSourceSerializer(serializers.ModelSerializer):
    """Serializer for NewsSource model"""
    class Meta:
        model = NewsSource
        fields = ['id', 'name', 'url', 'description', 'active', 'created_at', 'updated_at']

class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for NewsArticle model"""
    source = NewsSourceSerializer(read_only=True)
    stock_mentions = StockMentionSerializer(many=True, read_only=True)
    categories = ArticleCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'content', 'url', 'source', 'published_at',
            'author', 'summary', 'sentiment_score', 'is_processed',
            'stock_mentions', 'categories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['summary', 'sentiment_score', 'is_processed']

class NewsArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating NewsArticle"""
    source_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = NewsArticle
        fields = [
            'title', 'content', 'url', 'source_id', 'published_at',
            'author'
        ]

    def create(self, validated_data):
        source_id = validated_data.pop('source_id')
        try:
            source = NewsSource.objects.get(id=source_id)
        except NewsSource.DoesNotExist:
            raise serializers.ValidationError({'source_id': 'Invalid source ID'})
        
        validated_data['source'] = source
        return super().create(validated_data)

class NewsArticleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating NewsArticle"""
    class Meta:
        model = NewsArticle
        fields = ['title', 'content', 'published_at', 'author']
        read_only_fields = ['url', 'source']

class StockMentionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StockMention"""
    article_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StockMention
        fields = ['symbol', 'context', 'article_id']

    def create(self, validated_data):
        article_id = validated_data.pop('article_id')
        try:
            article = NewsArticle.objects.get(id=article_id)
        except NewsArticle.DoesNotExist:
            raise serializers.ValidationError({'article_id': 'Invalid article ID'})
        
        validated_data['article'] = article
        return super().create(validated_data)

class ArticleCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ArticleCategory"""
    article_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ArticleCategory
        fields = ['confidence_score', 'article_id', 'category_id']

    def create(self, validated_data):
        article_id = validated_data.pop('article_id')
        category_id = validated_data.pop('category_id')
        
        try:
            article = NewsArticle.objects.get(id=article_id)
            category = NewsCategory.objects.get(id=category_id)
        except (NewsArticle.DoesNotExist, NewsCategory.DoesNotExist):
            raise serializers.ValidationError({
                'article_id': 'Invalid article ID',
                'category_id': 'Invalid category ID'
            })
        
        validated_data['article'] = article
        validated_data['category'] = category
        return super().create(validated_data) 