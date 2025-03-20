from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.exceptions import Throttled
from django.core.cache import cache
from django.conf import settings

class CustomUserRateThrottle(UserRateThrottle):
    """Custom user rate throttle with dynamic rate limiting"""
    def allow_request(self, request, view):
        if request.user.is_staff:
            return True
        return super().allow_request(request, view)

    def wait(self):
        """Return the recommended wait time before the next request."""
        if not self.history:
            return 0

        remaining_duration = self.duration - (self.history[-1] - self.history[0])
        if remaining_duration <= 0:
            return 0

        return remaining_duration / float(len(self.history))

class CustomAnonRateThrottle(AnonRateThrottle):
    """Custom anonymous rate throttle with IP-based tracking"""
    def get_ident(self, request):
        """Identify the machine making the request by IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class CustomScopedRateThrottle(ScopedRateThrottle):
    """Custom scoped rate throttle with dynamic rate limiting"""
    def allow_request(self, request, view):
        if request.user.is_staff:
            return True

        # Get the rate limit from cache or settings
        rate = self.get_rate(request, view)
        if rate is None:
            return True

        self.rate = rate
        return super().allow_request(request, view)

    def get_rate(self, request, view):
        """Get the rate limit from cache or settings."""
        cache_key = f"{settings.CACHE_KEY_PREFIX}:rate_limit:{view.scope}"
        rate = cache.get(cache_key)
        
        if rate is None:
            rate = self.get_rate_from_settings(view.scope)
            cache.set(cache_key, rate, settings.CACHE_TIMEOUT)
        
        return rate

    def get_rate_from_settings(self, scope):
        """Get the rate limit from settings."""
        return self.THROTTLE_RATES.get(scope, '100/day')

class NewsIngestionThrottle(CustomScopedRateThrottle):
    """Throttle for news ingestion endpoints"""
    scope = 'news_ingestion'

    def allow_request(self, request, view):
        if request.user.is_staff:
            return True
        return super().allow_request(request, view)

class ArticleProcessingThrottle(CustomScopedRateThrottle):
    """Throttle for article processing endpoints"""
    scope = 'article_processing'

    def allow_request(self, request, view):
        if request.user.is_staff:
            return True
        return super().allow_request(request, view) 