# Smart City Data Hub | UAL | 2025-2026

A comprehensive backend system for collecting, processing, and serving urban data through ETL pipelines and a REST API. This project demonstrates modern data engineering practices for smart city applications, combining web scraping, API integration, and multi-database storage strategies.

## Overview

Smart City Data Hub is a Python-based backend system designed to aggregate and serve urban data from multiple sources. The system implements ETL (Extract, Transform, Load) pipelines to collect property and environmental data, storing it in both SQL and document databases for optimized querying and analysis.

## Features

### Data Collection
- **Property Data Collector**: Web scraping pipeline for extracting real estate information from property websites
- **Carbon Intensity Collector**: API integration for fuel usage and carbon intensity data

### Data Storage
- **Dual Database Architecture**: 
  - SQL database for structured, relational data queries
  - Document database for flexible, schema-less data storage
- **Optimised Data Models**: Designed for efficient retrieval and analysis

### REST API
- **Data Retrieval Endpoints**: Query stored urban data through RESTful interfaces
- **Calculation Services**: Real-time data processing and aggregation
- **User-Friendly Responses**: JSON-formatted data ready for frontend consumption

## Architecture

```
┌─────────────────┐
│  Data Sources   │
│  - Property Web │
│  - Carbon API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ETL Pipelines   │
│  - Scrapers     │
│  - Processors   │
│  - Validators   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Databases     │
│  - SQL (relat.) │
│  - Document DB  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   REST API      │
│  - Get Data     │
│  - Calculate    │
└─────────────────┘
```

## Technology Stack

- **Language**: Python 3.x
- **Web Scraping**: BeautifulSoup, Scrapy, or Selenium
- **API Framework**: FastAPI / Flask
- **Databases**: 
  - PostgreSQL (SQL)
  - MongoDB (Document)
- **Data Processing**: Pandas, NumPy
- **HTTP Requests**: Requests library

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or MySQL
- MongoDB
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/UAL-Lefteris/Smart-City-Data-Hub-2025-2026.git
cd Smart-City-Data-Hub-2025-2026
```

2. Create a virtual environment:
```bash
python -m .venv .venv

# Windows
.venv\Scripts\activate

# macOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
SQL_DATABASE_URL=postgresql://user:password@localhost:5432/smartcity
MONGO_DATABASE_URL=mongodb://localhost:27017/
MONGO_DATABASE_NAME=smartcity

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Running ETL Pipelines

**Property Data Collection:**
```bash
python -m collectors.property_collector
```

**Carbon Intensity Data Collection:**
```bash
python -m collectors.carbon_collector
```

### Starting the REST API

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`

## API Endpoints

### Property Data
- `GET /api/properties` - Retrieve all property listings
- `GET /api/properties/{id}` - Get specific property details
- `GET /api/properties/search` - Search properties by criteria

### Carbon Data
- `GET /api/carbon/current` - Get current carbon intensity
- `GET /api/carbon/forecast` - Get carbon intensity forecast
- `GET /api/carbon/history` - Historical carbon data

### Analytics
- `GET /api/analytics/property-stats` - Property market statistics
- `GET /api/analytics/carbon-trends` - Carbon intensity trends
- `GET /api/analytics/combined` - Combined urban analytics

## Project Structure

```
smart-city-data-hub/
├── api/
│   ├── __init__.py
│   ├── main.py              # API entry point
│   ├── routes/              # API route definitions
│   ├── models/              # Pydantic models
│   └── utils/               # API utilities
├── collectors/
│   ├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── tests/
│   ├── test_collectors.py
│   ├── test_api.py
│   └── test_etl.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Adding New Data Sources

1. Create a new collector in `collectors/`
2. Implement the ETL pipeline in `etl/`
3. Define data models in `database/`
4. Add API endpoints in `api/routes/`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Project Link: [https://github.com/yourusername/smart-city-data-hub](https://github.com/yourusername/smart-city-data-hub)

## Acknowledgments

- Carbon Intensity API providers
- Open data initiatives in smart cities
- Python data engineering community