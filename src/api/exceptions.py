from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class PropertyNotFoundException(Exception):
    def __init__(self, property_id: str):
        self.property_id = property_id
        self.message = f"Property with id {property_id} not found"
        super().__init__(self.message)


async def property_not_found_handler(
    request: Request,
    exc: PropertyNotFoundException
) -> JSONResponse:
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
