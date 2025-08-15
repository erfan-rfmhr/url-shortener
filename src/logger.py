import functools
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def log_request_info(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to log request source IP and timestamp for FastAPI router endpoints.

    This decorator extracts the client IP address and logs it along with the current
    timestamp when a request is made to the decorated endpoint.

    Args:
        func: The FastAPI router function to decorate

    Returns:
        The decorated function with request logging functionality
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the Request object in the function arguments
        request = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is not None:
            # Get client IP (handling potential proxy headers)
            client_ip = get_client_ip(request)
            timestamp = datetime.now().isoformat()

            # Log the request information
            logger.info(
                f"Request {request.method} {request.url.path} from IP: {client_ip} at {timestamp}"
            )
        else:
            # Fallback if Request object is not found
            timestamp = datetime.now().isoformat()
            logger.info(
                f"Request at {timestamp} - Request object not found in function parameters"
            )

        # Call the original function
        return await func(*args, **kwargs)

    return wrapper


def get_client_ip(request: Request) -> str:
    """
    Extract the client IP address from the request, considering proxy headers.

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address as string
    """
    # Check for common proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one (original client)
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to the direct client IP
    if request.client:
        return request.client.host

    return "unknown"
