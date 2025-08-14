import logging
import time

logger = logging.getLogger('assets')


class DetailedLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'Anonymous'

        logger.info(
            f"Incoming request: {request.method} {request.get_full_path()} by {username} | "
            f"Query params: {request.GET.dict()}"
        )

        try:
            response = self.get_response(request)
            duration = round(time.time() - start_time, 2)

            logger.info(
                f"Response: {request.method} {request.get_full_path()} by {username} | "
                f"Status: {response.status_code} | Duration: {duration}s | Response size: {len(response.content)}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Exception during request: {request.method} {request.get_full_path()} by {username} | "
                f"Error: {e}",
                exc_info=True
            )
            raise
