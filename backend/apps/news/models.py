from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .validators import NewsDataValidator

class NewsSource(models.Model):
    """Model for storing news sources"""
    name = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate source data"""
        data = {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'active': self.active
        }
        cleaned_data = NewsDataValidator.validate_source_data(data)
        self.name = cleaned_data['name']
        self.url = cleaned_data['url']
        self.description = cleaned_data['description']
        self.active = cleaned_data['active']

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    """Model for storing financial news articles"""
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(unique=True)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    author = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    embedding_vector = models.JSONField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate article data"""
        data = {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'author': self.author,
            'published_at': self.published_at
        }
        cleaned_data = NewsDataValidator.validate_article_data(data)
        self.title = cleaned_data['title']
        self.content = cleaned_data['content']
        self.url = cleaned_data['url']
        self.author = cleaned_data['author']
        self.published_at = cleaned_data['published_at']

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class StockMention(models.Model):
    """Model for tracking stock mentions in articles"""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='stock_mentions')
    symbol = models.CharField(max_length=10)
    context = models.TextField(blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate stock mention data"""
        self.symbol = NewsDataValidator.validate_stock_symbol(self.symbol)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.symbol} in {self.article.title}"

class NewsCategory(models.Model):
    """Model for categorizing news articles"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate category data"""
        data = {
            'name': self.name,
            'description': self.description
        }
        cleaned_data = NewsDataValidator.validate_category_data(data)
        self.name = cleaned_data['name']
        self.description = cleaned_data['description']

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ArticleCategory(models.Model):
    """Model for linking articles to categories"""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    confidence_score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "article categories"
        unique_together = ['article', 'category']

    def __str__(self):
        return f"{self.article.title} - {self.category.name}" 