import logging
import time

logger = logging.getLogger("assets")


class DetailedLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        try:
            response = self.get_response(request)
            duration = round(time.time() - start_time, 2)

            # Response log
            logger.info(
                f"[METHOD:{request.method}] - {request.get_full_path()} | "
                f"Query params: {request.GET.dict()}  | "
                f"Status: {response.status_code} | Duration: {duration}s | "
                f"Response size: {len(response.content)} bytes"
            )
            return response

        except Exception as e:
            # Exception log
            logger.error(
                f"[EXCEPTION] {request.method} {request.get_full_path()} | Error: {e}",
                exc_info=True,
            )
            raise
