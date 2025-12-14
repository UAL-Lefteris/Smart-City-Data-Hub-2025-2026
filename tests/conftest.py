import pytest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def mock_redis():
    import redis
    from unittest.mock import MagicMock

    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_redis_client.setex.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.keys.return_value = []

    original_from_url = redis.from_url
    redis.from_url = MagicMock(return_value=mock_redis_client)

    yield mock_redis_client

    redis.from_url = original_from_url
