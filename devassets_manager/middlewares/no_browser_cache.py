from django.utils.deprecation import MiddlewareMixin


class NoBrowserCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith("/api/"):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response
