import time
from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/cron/'):
            return self.get_response(request)

        ip = self._get_ip(request)
        key = f'ratelimit:{ip}'
        hits = cache.get(key, 0)
        if hits >= 120:
            return JsonResponse({'error': 'Rate limit exceeded. Try again later.'}, status=429)
        cache.set(key, hits + 1, 60)
        return self.get_response(request)

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
