from typing import Any, Dict, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.views import exception_handler as drf_exception_handler

from .responses import api_response


def custom_exception_handler(exc: Exception, context: Dict[str, Any]):
    """Return errors in a consistent envelope for the frontend.

    This wraps DRF's default exception handler so we still get correct
    status codes and validation error structures, but always inside:

        {"success": false, "message": str, "errors": {...}}
    """

    response = drf_exception_handler(exc, context)

    # If DRF didn't handle it, treat as 500.
    if response is None:
        return api_response(
            data=None,
            message=_("Internal server error"),
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=None,
        )

    default_detail: Optional[Any] = getattr(exc, "detail", None)

    # Map common exception types to friendly messages and codes
    if isinstance(exc, exceptions.ValidationError):
        message = _("Validation error")
    elif isinstance(exc, exceptions.AuthenticationFailed):
        message = _("Invalid credentials")
    elif isinstance(exc, exceptions.NotAuthenticated):
        message = _("Authentication credentials were not provided or are invalid")
    elif isinstance(exc, exceptions.PermissionDenied):
        message = _("You do not have permission to perform this action")
    elif isinstance(exc, exceptions.NotFound):
        message = _("Resource not found")
    else:
        # Fallback to DRF/exception detail text
        message = str(default_detail) if default_detail is not None else _("Error")

    return api_response(
        data=None,
        message=message,
        success=False,
        status_code=response.status_code,
        errors=response.data,
    )
