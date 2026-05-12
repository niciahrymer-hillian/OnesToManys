"""[FILE] test_manufacturers_api_annotated_cp.py

[WHY]
Integration tests validate HTTP endpoints handle requests/responses correctly.

[EFFECT]
Ensures end-to-end flows work: HTTP -> serialization -> database -> JSON response.
"""

import json
import pytest
from decimal import Decimal


# [CLASS] Test GET /api/manufacturers endpoints.
class TestManufacturerGetEndpoints:
    """[WHY] Verify retrieval operations work at HTTP layer.
    """

    # [TEST][POSITIVE][EDGE_CASE] Empty database.
    def test_should_return_empty_list_when_no_manufacturers_exist(self, client):
        """
        [ARRANGE] Fresh database via fixture.
        [ACT] GET /api/manufacturers
        [ASSERT] Returns 200 with empty array.
        
        [WHY] Edge case: app must handle empty results gracefully.
        """
        response = client.get("/api/manufacturers")
        assert response.status_code == 200
        assert response.json == []

    # [TEST][POSITIVE] Standard list retrieval.
    def test_should_return_all_manufacturers(self, client, sample_manufacturer):
        """
        [ARRANGE] One manufacturer via fixture.
        [ACT] GET /api/manufacturers
        [ASSERT] Returns array with one item.
        """
        response = client.get("/api/manufacturers")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["name"] == "TestCorp"

    # [TEST][POSITIVE] Single resource retrieval.
    def test_should_return_single_manufacturer_by_id(self, client, sample_manufacturer):
        """
        [ARRANGE] One manufacturer exists.
        [ACT] GET /api/manufacturers/{id}
        [ASSERT] Returns that specific manufacturer.
        
        [WHY] Route parameter handling; verify ID lookup works.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        response = client.get(f"/api/manufacturers/{mfg_id}")

        assert response.status_code == 200
        assert response.json["manufacturer_id"] == mfg_id
        assert response.json["name"] == "TestCorp"
        assert response.json["country"] == "USA"

    # [TEST][NEGATIVE] Resource not found.
    def test_should_return_404_when_manufacturer_not_found(self, client):
        """
        [ARRANGE] No manufacturer with ID 999.
        [ACT] GET /api/manufacturers/999
        [ASSERT] Returns 404 Not Found.
        
        [WHY] Verify error handling for missing resources.
        """
        response = client.get("/api/manufacturers/999")
        assert response.status_code == 404


# [CLASS] Test POST /api/manufacturers (create).
class TestManufacturerPostEndpoint:
    """[WHY] Verify resource creation with validation.
    """

    # [TEST][POSITIVE] Standard creation.
    def test_should_create_manufacturer_with_valid_data(self, client):
        """
        [ARRANGE] Valid JSON payload.
        [ACT] POST /api/manufacturers
        [ASSERT] Returns 201; response includes auto-generated ID.
        
        [WHY] Verify endpoint creates resource and returns it.
        """
        payload = {
            "name": "NewCorp",
            "country": "Germany",
            "founded_year": 1995,
            "headquarters_city": "Berlin",
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 201
        # [VERIFY] ID auto-generated.
        assert response.json["manufacturer_id"] is not None
        assert response.json["name"] == "NewCorp"
        # [VERIFY] Default is_active=True applied.
        assert response.json["is_active"] is True

    # [TEST][NEGATIVE][VALIDATION] Missing required field.
    def test_should_return_400_when_missing_required_field(self, client):
        """
        [ARRANGE] Payload missing 'name' field.
        [ACT] POST /api/manufacturers
        [ASSERT] Returns 400 Bad Request with error message.
        
        [WHY] Validate input validation works; prevents incomplete data.
        """
        payload = {
            "country": "France",
            "founded_year": 2000,
            "headquarters_city": "Paris",
            # Missing: name
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        # [VERIFY] Error message mentions missing field.
        assert "name" in response.json["error"]

    # [TEST][NEGATIVE][CONSTRAINT] Duplicate name.
    def test_should_return_409_when_name_already_exists(self, client, sample_manufacturer):
        """
        [ARRANGE] Manufacturer "TestCorp" already exists via fixture.
        [ACT] POST with same name.
        [ASSERT] Returns 409 Conflict.
        
        [WHY] Test unique constraint enforcement at HTTP layer.
        """
        payload = {
            "name": "TestCorp",  # Duplicate.
            "country": "Italy",
            "founded_year": 2010,
            "headquarters_city": "Rome",
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 409
        assert "error" in response.json
        # [VERIFY] Error mentions uniqueness.
        assert "unique" in response.json["error"].lower()

    # [TEST][POSITIVE][OPTIONAL_FIELD] Optional is_active parameter.
    def test_should_accept_optional_is_active_field(self, client):
        """
        [ARRANGE] Payload with is_active=False.
        [ACT] POST /api/manufacturers
        [ASSERT] Created manufacturer has is_active=False.
        
        [WHY] Verify optional fields are respected.
        """
        payload = {
            "name": "InactiveCorp",
            "country": "Spain",
            "founded_year": 2005,
            "headquarters_city": "Madrid",
            "is_active": False,  # Optional.
        }
        response = client.post("/api/manufacturers", json=payload)

        assert response.status_code == 201
        # [VERIFY] Optional field respected.
        assert response.json["is_active"] is False


# [CLASS] Test PUT /api/manufacturers/{id} (update).
class TestManufacturerPutEndpoint:
    """[WHY] Verify partial and full updates work correctly.
    """

    # [TEST][POSITIVE] Partial update (only some fields).
    def test_should_update_manufacturer_fields(self, client, sample_manufacturer):
        """
        [ARRANGE] Existing manufacturer.
        [ACT] PUT with only name, country, is_active (not founded_year).
        [ASSERT] Those fields changed; others unchanged.
        
        [WHY] Verify partial updates don't wipe untouched fields.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        payload = {
            "name": "UpdatedCorp",
            "country": "Japan",
            "is_active": False,
            # Note: founded_year NOT in payload.
        }
        response = client.put(f"/api/manufacturers/{mfg_id}", json=payload)

        assert response.status_code == 200
        # [VERIFY] Changed fields.
        assert response.json["name"] == "UpdatedCorp"
        assert response.json["country"] == "Japan"
        assert response.json["is_active"] is False
        # [VERIFY] Untouched field unchanged.
        assert response.json["founded_year"] == 2020

    # [TEST][NEGATIVE] Update non-existent resource.
    def test_should_return_404_when_updating_nonexistent_manufacturer(self, client):
        """
        [ARRANGE] No manufacturer with ID 999.
        [ACT] PUT /api/manufacturers/999
        [ASSERT] Returns 404.
        """
        payload = {"name": "NewName"}
        response = client.put("/api/manufacturers/999", json=payload)

        assert response.status_code == 404

    # [TEST][NEGATIVE][CONSTRAINT] Update to duplicate name.
    def test_should_return_409_when_updating_to_duplicate_name(
        self, client, sample_manufacturer
    ):
        """
        [ARRANGE] Two manufacturers exist: "TestCorp" and "OtherCorp".
        [ACT] PUT TestCorp's name to "OtherCorp".
        [ASSERT] Returns 409 Conflict (unique constraint violation).
        
        [WHY] Test update validation; can't rename to existing name.
        """
        # [SETUP] Create second manufacturer.
        other_payload = {
            "name": "OtherCorp",
            "country": "Canada",
            "founded_year": 2015,
            "headquarters_city": "Toronto",
        }
        client.post("/api/manufacturers", json=other_payload)

        # [ACT] Try to rename first to second's name.
        mfg_id = sample_manufacturer.manufacturer_id
        update_payload = {"name": "OtherCorp"}
        response = client.put(f"/api/manufacturers/{mfg_id}", json=update_payload)

        # [ASSERT] Conflict detected.
        assert response.status_code == 409


# [CLASS] Test DELETE /api/manufacturers/{id}.
class TestManufacturerDeleteEndpoint:
    """[WHY] Verify deletion removes resource and cannot be re-accessed.
    """

    # [TEST][POSITIVE] Standard deletion.
    def test_should_delete_manufacturer(self, client, sample_manufacturer):
        """
        [ARRANGE] Existing manufacturer.
        [ACT] DELETE /api/manufacturers/{id}
        [ASSERT] Returns 200 with success message.
        [THEN] GET same ID returns 404.
        
        [WHY] Verify resource is actually removed.
        """
        mfg_id = sample_manufacturer.manufacturer_id
        response = client.delete(f"/api/manufacturers/{mfg_id}")

        # [VERIFY] Deletion response.
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()

        # [VERIFY] Resource gone.
        get_response = client.get(f"/api/manufacturers/{mfg_id}")
        assert get_response.status_code == 404

    # [TEST][NEGATIVE] Delete non-existent resource.
    def test_should_return_404_when_deleting_nonexistent_manufacturer(self, client):
        """
        [ARRANGE] No manufacturer with ID 999.
        [ACT] DELETE /api/manufacturers/999
        [ASSERT] Returns 404.
        
        [WHY] Verify safe deletion; no error on missing resource.
        """
        response = client.delete("/api/manufacturers/999")
        assert response.status_code == 404
