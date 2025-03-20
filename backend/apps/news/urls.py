from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sources', views.NewsSourceViewSet)
router.register(r'articles', views.NewsArticleViewSet)
router.register(r'stock-mentions', views.StockMentionViewSet)
router.register(r'categories', views.NewsCategoryViewSet)
router.register(r'article-categories', views.ArticleCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 