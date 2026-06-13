from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.error_messages import ERROR_MESSAGES


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Catches all HTTPExceptions and returns consistent JSON.
    Example: 404 → {"error": "Not Found", "detail": "Product not found", "path": "/api/v1/products/99"}
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            # "path": str(request.url.path), This will return route
            "status_code": exc.status_code,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches Pydantic validation errors (wrong field types, missing fields)
    and returns a clean, readable error response.
    """
    errors = []
    for error in exc.errors():
        # remove prefix
        message = error["msg"].replace("Value error, ", "")
        error_type = error["type"].split(".")[-1]  # e.g. "value_error.missing" → "missing"
        field = " → ".join(str(loc) for loc in error["loc"]) # It contain this kind of error format: "field": "body → password"

        # Handle missing field errors
        if error_type == "missing":

            field_messages = {
                "name": ERROR_MESSAGES["NAME_REQUIRED"],
                "password": ERROR_MESSAGES["PASSWORD_REQUIRED"],
                "email": ERROR_MESSAGES["EMAIL_INVALID"]
            }

            message = field_messages.get(
                field,
                "This field is required."
            )

        errors.append({"message": message})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "details": errors,
            "path": str(request.url.path),
        },
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches any unexpected Python error so the server never crashes
    and never leaks a stack trace to the client.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": str(exc),
            "path": str(request.url.path),
        },
    )
