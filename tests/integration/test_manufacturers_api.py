"""Integration tests for Manufacturer API endpoints.

Why: Ensures all CRUD operations work correctly through HTTP.
Effect: Validates end-to-end request/response flow and error handling.
"""

import json
import pytest
from decimal import Decimal


class TestManufacturerGetEndpoints:
    """Test GET endpoints for manufacturers."""

    def test_should_return_empty_list_when_no_manufacturers_exist(self, client):
        """
        Arrange: Fresh database with no manufacturers.
        Act: GET /api/manufacturers
        Assert: Returns empty JSON array with 200 status.
        """
        response = client.get("/api/manufacturers")
        assert response.status_code == 200
        assert response.json == []

    def test_should_return_all_manufacturers(self, client, sample_manufacturer):
        """
        Arrange: One sample manufacturer exists.
        Act: GET /api/manufacturers
        Assert: Returns array with one manufacturer object.
        """
        response = client.get("/api/manufacturers")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["name"] == "TestCorp"

    def test_should_return_single_manufacturer_by_id(self, client, sample_manufacturer):
        """
        Arrange: One sample manufacturer exists.
        Act: GET /api/manufacturers/{id}
        Assert: Returns the manufacturer object with correct fields.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        response = client.get(f"/api/manufacturers/{mfg_id}")

        assert response.status_code == 200
        assert response.json["manufacturer_id"] == mfg_id
        assert response.json["name"] == "TestCorp"
        assert response.json["country"] == "USA"

    def test_should_return_404_when_manufacturer_not_found(self, client):
        """
        Arrange: No manufacturer with ID 999 exists.
        Act: GET /api/manufacturers/999
        Assert: Returns 404 Not Found.
        """
        response = client.get("/api/manufacturers/999")
        assert response.status_code == 404


class TestManufacturerPostEndpoint:
    """Test POST endpoint for creating manufacturers."""

    def test_should_create_manufacturer_with_valid_data(self, client):
        """
        Arrange: Valid manufacturer JSON.
        Act: POST /api/manufacturers
        Assert: Returns 201 with created manufacturer including ID.
        """
        payload = {
            "name": "NewCorp",
            "country": "Germany",
            "founded_year": 1995,
            "headquarters_city": "Berlin",
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 201
        assert response.json["manufacturer_id"] is not None
        assert response.json["name"] == "NewCorp"
        assert response.json["is_active"] is True

    def test_should_return_400_when_missing_required_field(self, client):
        """
        Boundary case: Missing required field.
        Act: POST without 'name'.
        Assert: Returns 400 with error message.
        """
        payload = {
            "country": "France",
            "founded_year": 2000,
            "headquarters_city": "Paris",
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "name" in response.json["error"]

    def test_should_return_409_when_name_already_exists(self, client, sample_manufacturer):
        """
        Negative scenario: Duplicate manufacturer name.
        Act: POST with existing name.
        Assert: Returns 409 Conflict.
        """
        payload = {
            "name": "TestCorp",  # Duplicate
            "country": "Italy",
            "founded_year": 2010,
            "headquarters_city": "Rome",
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 409
        assert "error" in response.json
        assert "unique" in response.json["error"].lower()

    def test_should_accept_optional_is_active_field(self, client):
        """
        Arrange: Payload with is_active=False.
        Act: POST /api/manufacturers
        Assert: Created manufacturer has is_active=False.
        """
        payload = {
            "name": "InactiveCorp",
            "country": "Spain",
            "founded_year": 2005,
            "headquarters_city": "Madrid",
            "is_active": False,
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 201
        assert response.json["is_active"] is False


class TestManufacturerPutEndpoint:
    """Test PUT endpoint for updating manufacturers."""

    def test_should_update_manufacturer_fields(self, client, sample_manufacturer):
        """
        Arrange: Existing manufacturer with sample data.
        Act: PUT with updated fields.
        Assert: Returns updated manufacturer.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        payload = {
            "name": "UpdatedCorp",
            "country": "Japan",
            "is_active": False,
        }
        response = client.put(f"/api/manufacturers/{mfg_id}", json=payload)

        assert response.status_code == 200
        assert response.json["name"] == "UpdatedCorp"
        assert response.json["country"] == "Japan"
        assert response.json["is_active"] is False
        assert response.json["founded_year"] == 2020  # Unchanged

    def test_should_return_404_when_updating_nonexistent_manufacturer(self, client):
        """
        Negative scenario: Update non-existent manufacturer.
        Act: PUT /api/manufacturers/999
        Assert: Returns 404.
        """
        payload = {"name": "NewName"}
        response = client.put("/api/manufacturers/999", json=payload)

        assert response.status_code == 404

    def test_should_return_409_when_updating_to_duplicate_name(
        self, client, sample_manufacturer
    ):
        """
        Negative scenario: Update name to one that already exists.
        Act: Create second manufacturer, then PUT first to second's name.
        Assert: Returns 409 Conflict.
        """
        # Create a second manufacturer
        other_payload = {
            "name": "OtherCorp",
            "country": "Canada",
            "founded_year": 2015,
            "headquarters_city": "Toronto",
        }
        client.post("/api/manufacturers", json=other_payload)

        # Try to rename first to second's name
        mfg_id = sample_manufacturer.manufacturer_id
        update_payload = {"name": "OtherCorp"}
        response = client.put(f"/api/manufacturers/{mfg_id}", json=update_payload)

        assert response.status_code == 409


class TestManufacturerDeleteEndpoint:
    """Test DELETE endpoint for manufacturers."""

    def test_should_delete_manufacturer(self, client, sample_manufacturer):
        """
        Arrange: Existing manufacturer.
        Act: DELETE /api/manufacturers/{id}
        Assert: Returns 200 with success message, then GET returns 404.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        response = client.delete(f"/api/manufacturers/{mfg_id}")

        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()

        # Verify deletion
        get_response = client.get(f"/api/manufacturers/{mfg_id}")
        assert get_response.status_code == 404

    def test_should_return_404_when_deleting_nonexistent_manufacturer(self, client):
        """
        Negative scenario: Delete non-existent manufacturer.
        Act: DELETE /api/manufacturers/999
        Assert: Returns 404.
        """
        response = client.delete("/api/manufacturers/999")
        assert response.status_code == 404
