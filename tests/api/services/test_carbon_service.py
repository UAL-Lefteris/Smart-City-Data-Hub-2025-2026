import pytest
from unittest.mock import Mock, MagicMock
from bson import ObjectId
from fastapi import HTTPException

from src.api.services.carbon_service import CarbonService


class TestSerializeMongoData:
    """
    Unit tests for the _serialize_mongo_data method (SIMPLE FUNCTION)

    This function converts MongoDB ObjectId fields to strings for JSON serialization.
    These tests demonstrate basic pytest usage with straightforward test cases.
    """

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.service = CarbonService(self.mock_db)

    def test_serialize_single_item_with_id(self):
        """Test serialization of a single item containing an _id field"""
        test_id = ObjectId()
        data = [{"_id": test_id, "name": "test"}]

        result = self.service._serialize_mongo_data(data)

        assert result[0]["_id"] == str(test_id)
        assert result[0]["name"] == "test"
        assert isinstance(result[0]["_id"], str)

    def test_serialize_multiple_items_with_ids(self):
        """Test serialization of multiple items with _id fields"""
        test_id_1 = ObjectId()
        test_id_2 = ObjectId()
        data = [
            {"_id": test_id_1, "region": 1},
            {"_id": test_id_2, "region": 2}
        ]

        result = self.service._serialize_mongo_data(data)

        assert len(result) == 2
        assert result[0]["_id"] == str(test_id_1)
        assert result[1]["_id"] == str(test_id_2)
        assert all(isinstance(item["_id"], str) for item in result)

    def test_serialize_empty_list(self):
        """Test serialization with an empty list"""
        data = []

        result = self.service._serialize_mongo_data(data)

        assert result == []
        assert isinstance(result, list)

    def test_serialize_items_without_id(self):
        """Test serialization of items that don't have _id fields"""
        data = [
            {"name": "test1", "value": 100},
            {"name": "test2", "value": 200}
        ]

        result = self.service._serialize_mongo_data(data)

        assert result == data
        assert "_id" not in result[0]
        assert "_id" not in result[1]

    def test_serialize_mixed_items(self):
        """Test serialization with mix of items with and without _id"""
        test_id = ObjectId()
        data = [
            {"_id": test_id, "name": "with_id"},
            {"name": "without_id", "value": 42}
        ]

        result = self.service._serialize_mongo_data(data)

        assert result[0]["_id"] == str(test_id)
        assert "_id" not in result[1]
        assert result[1]["value"] == 42

    def test_serialize_preserves_other_fields(self):
        """Test that serialization preserves all other fields unchanged"""
        test_id = ObjectId()
        data = [{
            "_id": test_id,
            "region_id": 123,
            "postcode": "SW1A 1AA",
            "intensity": 250,
            "renewable_percentage": 45.5,
            "nested": {"key": "value"}
        }]

        result = self.service._serialize_mongo_data(data)

        assert result[0]["region_id"] == 123
        assert result[0]["postcode"] == "SW1A 1AA"
        assert result[0]["intensity"] == 250
        assert result[0]["renewable_percentage"] == 45.5
        assert result[0]["nested"] == {"key": "value"}


class TestSearchCarbonData:
    """
    Unit tests for the search_carbon_data method (COMPLEX FUNCTION)

    This function performs complex searches with multiple validation rules and
    repository interactions. These tests demonstrate advanced pytest usage including:
    - Mocking dependencies
    - Testing validation logic
    - Exception handling
    - Multiple code paths
    """

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.service = CarbonService(self.mock_db)
        self.service.repository = Mock()

    def test_search_with_valid_intensity_index(self):
        """Test search with a valid intensity_index parameter"""
        mock_data = [
            {"_id": ObjectId(), "region_id": 1, "intensity_index": "low"}
        ]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data(intensity_index="low")

        assert result["total"] == 1
        assert result["data"][0]["intensity_index"] == "low"
        assert "filters" in result
        assert result["filters"]["intensity_index"] == "low"

    def test_search_with_invalid_intensity_index(self):
        """Test that invalid intensity_index raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            self.service.search_carbon_data(intensity_index="invalid")

        assert exc_info.value.status_code == 400
        assert "Invalid intensity_index" in exc_info.value.detail
        assert "low, moderate, high, very high" in exc_info.value.detail

    def test_search_with_max_intensity_less_than_min(self):
        """Test that max_intensity < min_intensity raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            self.service.search_carbon_data(min_intensity=300, max_intensity=100)

        assert exc_info.value.status_code == 400
        assert "max_intensity must be greater than or equal to min_intensity" in exc_info.value.detail

    def test_search_with_valid_intensity_range(self):
        """Test search with valid intensity range"""
        mock_data = [{"_id": ObjectId(), "intensity": 250}]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data(min_intensity=200, max_intensity=300)

        assert result["filters"]["min_intensity"] == 200
        assert result["filters"]["max_intensity"] == 300
        self.service.repository.search.assert_called_once()

    def test_search_with_max_renewable_less_than_min(self):
        """Test that max_renewable < min_renewable raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            self.service.search_carbon_data(min_renewable=80.0, max_renewable=20.0)

        assert exc_info.value.status_code == 400
        assert "max_renewable must be greater than or equal to min_renewable" in exc_info.value.detail

    def test_search_with_valid_renewable_range(self):
        """Test search with valid renewable percentage range"""
        mock_data = [{"_id": ObjectId(), "renewable_percentage": 45.5}]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data(min_renewable=40.0, max_renewable=50.0)

        assert result["filters"]["min_renewable"] == 40.0
        assert result["filters"]["max_renewable"] == 50.0

    def test_search_with_all_parameters(self):
        """Test search with all available parameters"""
        mock_data = [
            {
                "_id": ObjectId(),
                "region_id": 5,
                "postcode": "SW1A 1AA",
                "intensity": 275,
                "intensity_index": "moderate",
                "renewable_percentage": 42.0
            }
        ]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data(
            region_id=5,
            postcode="SW1A 1AA",
            min_intensity=200,
            max_intensity=300,
            intensity_index="moderate",
            min_renewable=40.0,
            max_renewable=50.0,
            skip=10,
            limit=50
        )

        assert result["total"] == 1
        assert result["skip"] == 10
        assert result["limit"] == 50
        assert result["filters"]["region_id"] == 5
        assert result["filters"]["postcode"] == "SW1A 1AA"
        assert result["filters"]["intensity_index"] == "moderate"

        self.service.repository.search.assert_called_once_with(
            region_id=5,
            postcode="SW1A 1AA",
            min_intensity=200,
            max_intensity=300,
            intensity_index="moderate",
            min_renewable=40.0,
            max_renewable=50.0,
            skip=10,
            limit=50
        )

    def test_search_serializes_object_ids(self):
        """Test that search results properly serialize MongoDB ObjectIds"""
        test_id = ObjectId()
        mock_data = [{"_id": test_id, "region_id": 1}]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data(region_id=1)

        assert isinstance(result["data"][0]["_id"], str)
        assert result["data"][0]["_id"] == str(test_id)

    def test_search_with_no_results(self):
        """Test search that returns no results"""
        self.service.repository.search.return_value = ([], 0)

        result = self.service.search_carbon_data(region_id=999)

        assert result["total"] == 0
        assert result["data"] == []
        assert result["filters"]["region_id"] == 999

    def test_search_with_pagination(self):
        """Test search with pagination parameters"""
        mock_data = [{"_id": ObjectId(), "region_id": i} for i in range(5)]
        self.service.repository.search.return_value = (mock_data, 100)

        result = self.service.search_carbon_data(skip=20, limit=5)

        assert result["skip"] == 20
        assert result["limit"] == 5
        assert result["total"] == 100
        assert len(result["data"]) == 5

    def test_search_repository_raises_exception(self):
        """Test that repository exceptions are properly handled"""
        self.service.repository.search.side_effect = Exception("Database connection error")

        with pytest.raises(HTTPException) as exc_info:
            self.service.search_carbon_data(region_id=1)

        assert exc_info.value.status_code == 500
        assert "Error searching carbon data" in exc_info.value.detail

    def test_search_case_insensitive_intensity_index(self):
        """Test that intensity_index validation is case-insensitive"""
        mock_data = [{"_id": ObjectId(), "intensity_index": "high"}]
        self.service.repository.search.return_value = (mock_data, 1)

        # These should all be valid
        for index in ["LOW", "Low", "MODERATE", "Moderate", "HIGH", "High", "VERY HIGH", "Very High"]:
            result = self.service.search_carbon_data(intensity_index=index)
            assert result is not None

    def test_search_returns_correct_structure(self):
        """Test that search returns the correct response structure"""
        mock_data = [{"_id": ObjectId(), "region_id": 1}]
        self.service.repository.search.return_value = (mock_data, 1)

        result = self.service.search_carbon_data()

        assert "data" in result
        assert "total" in result
        assert "skip" in result
        assert "limit" in result
        assert "filters" in result
        assert isinstance(result["data"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["filters"], dict)
