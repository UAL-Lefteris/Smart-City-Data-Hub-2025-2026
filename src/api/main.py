from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.database.connection import engine, Base
from src.api.routes import properties
from src.api.exceptions import (
    PropertyNotFoundException,
    property_not_found_handler,
    validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
    - Creates all database tables if they don't exist

    Shutdown:
    - Closes database connections
    """
    Base.metadata.create_all(bind=engine)

    yield

    engine.dispose()


app = FastAPI(
    title="Urban Data Hub API",
    description="""
    ## London Property Data API

    This API provides access to London property data for the BSc Data Science course.

    ### Features:
    * **CRUD Operations**: Create, Read, Update, and Delete property records
    * **Search & Filter**: Search properties by borough, price range, and bedrooms
    * **Pagination**: Efficient data retrieval with limit and offset parameters
    * **Data Validation**: Automatic validation using Pydantic models

    ### Resources:
    * **Properties**: Manage London property listings

    ### Learning Objectives:
    This API demonstrates:
    - RESTful API design principles
    - HTTP methods and status codes
    - Request/Response handling
    - Database integration with SQLAlchemy
    - Data validation and serialization
    """,
    version="1.0.0",
    contact={
        "name": "Data Science Course",
        "email": "datasci@example.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(PropertyNotFoundException, property_not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(
    properties.router,
    prefix="/properties",
    tags=["Properties"],
)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check and welcome message.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to Urban Data Hub API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: API health status
    """
    return {
        "status": "healthy",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
