from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import time


class SimpleRateLimitMiddleware(MiddlewareMixin):
    """Very small per-IP rate limit middleware.

    Configure limit by adding to settings.MIDDLEWARE.
    This defaults to 1 request per 2 seconds per IP for POST endpoints.
    """

    def process_request(self, request):
        if request.method != 'POST':
            return None
        ip = request.META.get('REMOTE_ADDR') or 'anonymous'
        key = f'rl:{ip}'
        now = time.time()
        window = 2  # seconds
        allowed = 1
        data = cache.get(key)
        if data:
            timestamps = data
            # purge old
            timestamps = [t for t in timestamps if now - t < window]
        else:
            timestamps = []
        if len(timestamps) >= allowed:
            return HttpResponse('Too many requests, slow down.', status=429)
        timestamps.append(now)
        cache.set(key, timestamps, timeout=window)
        return None
