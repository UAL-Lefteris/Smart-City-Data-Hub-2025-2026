"""
Utility functions for Carbon Intensity ETL Pipeline.

This module provides common utility functions used across the pipeline,
including logging setup, date handling, and data validation.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path


def setup_logging(log_level='INFO', log_file=None):
    """
    Setup logging configuration with colored console output and file logging.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to log file (optional)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('carbon_etl')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.handlers.clear()
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def parse_iso_datetime(datetime_str):
    """
    Parse ISO format datetime string to datetime object.
    
    Args:
        datetime_str (str): ISO format datetime string
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str[:-1] + '+00:00'
        return datetime.fromisoformat(datetime_str)
    except (ValueError, AttributeError):
        return None


def format_datetime_for_api(dt):
    """
    Format datetime object for API request.
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: Formatted datetime string (YYYY-MM-DDTHH:MM:SSZ)
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_date_range(start_date, end_date=None, days_back=7):
    """
    Generate a list of dates for querying.
    
    Args:
        start_date (datetime or str): Start date
        end_date (datetime or str): End date (optional)
        days_back (int): Number of days to go back if end_date not provided
        
    Returns:
        list: List of date strings in YYYY-MM-DD format
    """
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    
    if end_date is None:
        end_date = start_date + timedelta(days=days_back)
    elif isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list


def validate_postcode(postcode):
    """
    Basic validation for UK postcodes.
    
    Args:
        postcode (str): Postcode to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    postcode = postcode.replace(' ', '').upper()
    
    if len(postcode) < 5 or len(postcode) > 7:
        return False
    
    return True


def clean_postcode(postcode):
    """
    Clean and standardize postcode format.
    
    Args:
        postcode (str): Postcode to clean
        
    Returns:
        str: Cleaned postcode in standard format
    """
    cleaned = postcode.replace(' ', '').upper()
    
    if len(cleaned) >= 5:
        cleaned = f"{cleaned[:-3]} {cleaned[-3:]}"
    
    return cleaned


def calculate_intensity_index(intensity_value):
    """
    Calculate intensity index based on carbon intensity value.
    
    Index levels:
    - very low: 0-100 gCO2/kWh
    - low: 100-200 gCO2/kWh
    - moderate: 200-250 gCO2/kWh
    - high: 250-300 gCO2/kWh
    - very high: 300+ gCO2/kWh
    
    Args:
        intensity_value (float): Carbon intensity in gCO2/kWh
        
    Returns:
        str: Intensity index category
    """
    if intensity_value is None:
        return 'unknown'
    
    if intensity_value < 100:
        return 'very low'
    elif intensity_value < 200:
        return 'low'
    elif intensity_value < 250:
        return 'moderate'
    elif intensity_value < 300:
        return 'high'
    else:
        return 'very high'


def validate_carbon_data(data_dict):
    """
    Validate carbon intensity data structure.
    
    Args:
        data_dict (dict): Data dictionary to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['from', 'to', 'intensity']
    
    for field in required_fields:
        if field not in data_dict:
            return False
    
    intensity = data_dict.get('intensity', {})
    if not isinstance(intensity, dict):
        return False
    
    if 'forecast' not in intensity and 'actual' not in intensity:
        return False
    
    return True


def chunk_list(lst, chunk_size):
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (list): List to split
        chunk_size (int): Size of each chunk
        
    Yields:
        list: Chunks of the original list
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def safe_float_conversion(value, default=None):
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        float or default: Converted value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int_conversion(value, default=None):
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        int or default: Converted value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_stats(values):
    """
    Calculate basic statistics for a list of values.
    
    Args:
        values (list): List of numeric values
        
    Returns:
        dict: Dictionary with min, max, mean, median
    """
    if not values:
        return {
            'min': None,
            'max': None,
            'mean': None,
            'count': 0
        }
    
    return {
        'min': min(values),
        'max': max(values),
        'mean': sum(values) / len(values),
        'count': len(values)
    }


def get_current_timestamp():
    """
    Get current UTC timestamp in ISO format.
    
    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.utcnow().isoformat()


def create_unique_id(prefix, *parts):
    """
    Create a unique identifier from multiple parts.
    
    Args:
        prefix (str): Prefix for the ID
        *parts: Variable number of parts to include in ID
        
    Returns:
        str: Unique identifier
    """
    parts_str = '_'.join(str(p) for p in parts)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"{prefix}_{parts_str}_{timestamp}"
