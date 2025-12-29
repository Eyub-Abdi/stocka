from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.response import Response


def api_response(
    data: Optional[Any] = None,
    *,
    message: str = "",
    success: bool = True,
    status_code: int = 200,
    errors: Optional[Any] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Response:
    """Standard API response wrapper for consistent frontend handling.

    Structure:
        {
            "success": bool,
            "message": str,
            "data": ...,
            "errors": ...,
            "meta": {...}  # optional extra info such as pagination
        }
    """

    payload: Dict[str, Any] = {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }

    if extra:
        payload["meta"] = extra

    return Response(payload, status=status_code)
