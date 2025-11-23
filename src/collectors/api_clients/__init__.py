"""
Carbon Intensity ETL Pipeline - Source Package

This package contains the core ETL modules:
- extract: API data extraction
- transform: Data cleaning and transformation
- load: MongoDB operations
- utils: Utility functions
"""

__version__ = '1.0.0'
__author__ = 'Carbon Intensity ETL Team'

from .extract import CarbonIntensityExtractor
from .transform import CarbonIntensityTransformer
from .load import CarbonIntensityLoader
from .utils import setup_logging

__all__ = [
    'CarbonIntensityExtractor',
    'CarbonIntensityTransformer',
    'CarbonIntensityLoader',
    'setup_logging'
]
