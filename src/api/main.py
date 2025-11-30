from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database.database import database
from src.api.routes import properties, carbon
from src.api.exceptions import (
    PropertyNotFoundException,
    property_not_found_handler,
    validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_postgres_tables()

    yield

    database.close()


app = FastAPI(
    title="Urban Data Hub API",
    description="""
    ## Smart City Data Hub API

    This API provides access to London property and carbon intensity data.

    ### Features:
    * **Property Data**: CRUD operations for London property listings (PostgreSQL)
    * **Carbon Intensity Data**: Access to UK carbon intensity data (MongoDB)
    * **Search & Filter**: Advanced search and filtering capabilities
    * **Pagination**: Efficient data retrieval with limit and offset parameters
    * **Data Validation**: Automatic validation using Pydantic models

    ### Resources:
    * **Properties**: Manage London property listings from web scraping
    * **Carbon Intensity**: Access carbon intensity data by region and postcode

    ### Databases:
    - **PostgreSQL**: Property data storage
    - **MongoDB**: Carbon intensity data storage

    ### Learning Objectives:
    This API demonstrates:
    - RESTful API design principles
    - Multi-database integration (PostgreSQL + MongoDB)
    - HTTP methods and status codes
    - Request/Response handling
    - Data validation and serialization
    """,
    version="2.0.0",
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

app.include_router(
    carbon.router,
    prefix="/carbon",
    tags=["Carbon Intensity"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Urban Data Hub API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
