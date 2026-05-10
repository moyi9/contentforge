"""Security middleware for ContentForge API.

- Request body size limit (protects against OOM attacks)
- Optional API token authentication (disabled when token is empty)
"""

import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB


class ContentForgeSecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware that enforces body size limits and optional auth."""

    async def dispatch(self, request: Request, call_next):
        # Body size check for write methods
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large (max 10 MB)"},
                )

        # Optional API token check
        api_token = getattr(settings, "api_token", None) or getattr(settings, "API_TOKEN", None)
        if api_token:
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer ") or auth.removeprefix("Bearer ") != api_token:
                # Skip auth for CORS preflight and docs
                if request.method != "OPTIONS" and not request.url.path.startswith("/docs"):
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Missing or invalid API token"},
                    )

        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
