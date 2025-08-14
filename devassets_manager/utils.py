import logging
from rest_framework.views import exception_handler

logger = logging.getLogger('devassets_manager')
def custom_exception_handler(exc, context):
    """
    Logs all DRF exceptions with traceback.
    """
    response = exception_handler(exc, context)
    if response is not None:
        logger.error(
            f"Exception: {exc} | View: {context.get('view')} | Request: {context.get('request')}",
            exc_info=True
        )
    return response
