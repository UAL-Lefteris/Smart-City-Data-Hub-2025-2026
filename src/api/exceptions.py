from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class PropertyNotFoundException(Exception):
    """
    Exception raised when a property is not found.

    This is a custom exception that can be raised anywhere
    in the application when a property lookup fails.
    """

    def __init__(self, property_id: int):
        """
        Initialize exception with property ID.

        Args:
            property_id: ID of the property that was not found
        """
        self.property_id = property_id
        self.message = f"Property with id {property_id} not found"
        super().__init__(self.message)


async def property_not_found_handler(
    request: Request,
    exc: PropertyNotFoundException
) -> JSONResponse:
    """
    Handle PropertyNotFoundException.

    Args:
        request: FastAPI request object
        exc: The exception that was raised

    Returns:
        JSONResponse: 404 response with error details

    Example Response:
        {
            "error": "Not Found",
            "message": "Property with id 123 not found",
            "property_id": 123,
            "path": "/properties/123"
        }
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "property_id": exc.property_id,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle validation errors from Pydantic.

    This handler provides detailed information about
    what validation failed and why.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSONResponse: 422 response with validation error details

    Example Response:
        {
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": [
                {
                    "field": "price",
                    "message": "Price must be greater than 0",
                    "type": "value_error"
                }
            ],
            "path": "/properties"
        }
    """
    errors = []

    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])

        errors.append({
            "field": field or "body",
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": errors,
            "path": str(request.url.path),
        },
    )
