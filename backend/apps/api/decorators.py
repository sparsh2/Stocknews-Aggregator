from functools import wraps
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response

def cache_response(timeout=None, key_prefix=None):
    """
    Decorator to cache API responses.
    
    Args:
        timeout (int): Cache timeout in seconds. If None, uses default timeout.
        key_prefix (str): Prefix for cache key. If None, uses default prefix.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(request, view_instance, key_prefix)
            
            # Try to get response from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return Response(cached_response)
            
            # Get response from view
            response = view_func(view_instance, request, *args, **kwargs)
            
            # Cache the response
            if response.status_code == 200:
                cache_timeout = timeout or settings.CACHE_TIMEOUT
                cache.set(cache_key, response.data, cache_timeout)
            
            return response
        return _wrapped_view
    return decorator

def generate_cache_key(request, view_instance, key_prefix=None):
    """Generate a unique cache key for the request."""
    prefix = key_prefix or settings.CACHE_KEY_PREFIX
    path = request.path
    method = request.method
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    
    # Include query parameters in cache key
    query_params = request.query_params
    if query_params:
        query_string = '&'.join(f"{k}={v}" for k, v in sorted(query_params.items()))
        path = f"{path}?{query_string}"
    
    return f"{prefix}:{method}:{path}:{user_id}"

def invalidate_cache(pattern):
    """
    Decorator to invalidate cache entries matching a pattern.
    
    Args:
        pattern (str): Pattern to match cache keys for invalidation.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            response = view_func(view_instance, request, *args, **kwargs)
            
            if response.status_code in [200, 201, 204]:
                # Invalidate cache entries matching the pattern
                cache_pattern = f"{settings.CACHE_KEY_PREFIX}:{pattern}"
                keys = cache.keys(cache_pattern)
                if keys:
                    cache.delete_many(keys)
            
            return response
        return _wrapped_view
    return decorator 