"""[FILE] test_products_api_annotated_cp.py

[WHY]
Integration tests for product endpoint validate HTTP layer and FK relationships.

[EFFECT]
Ensures products respect manufacturer relationships and cascade behavior.
"""

import json
import pytest
from decimal import Decimal


# [CLASS] Test GET /api/products endpoints.
class TestProductGetEndpoints:
    """[WHY] Verify product retrieval at HTTP layer.
    """

    # [TEST][POSITIVE][EDGE_CASE] Empty list.
    def test_should_return_empty_list_when_no_products_exist(self, client):
        """
        [ARRANGE] Fresh database.
        [ACT] GET /api/products
        [ASSERT] Returns 200 with empty array.
        
        [WHY] Edge case: handle empty results gracefully.
        """
        response = client.get("/api/products")
        assert response.status_code == 200
        assert response.json == []

    # [TEST][POSITIVE] List all products.
    def test_should_return_all_products(self, client, sample_product):
        """
        [ARRANGE] One product via fixture.
        [ACT] GET /api/products
        [ASSERT] Returns array with that product.
        """
        response = client.get("/api/products")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["product_name"] == "TestProduct"

    # [TEST][POSITIVE] Get single product.
    def test_should_return_single_product_by_id(self, client, sample_product):
        """
        [ARRANGE] One product exists.
        [ACT] GET /api/products/{id}
        [ASSERT] Returns that product with all fields.
        """
        product_id = sample_product.product_id
        response = client.get(f"/api/products/{product_id}")

        assert response.status_code == 200
        assert response.json["product_id"] == product_id
        assert response.json["product_name"] == "TestProduct"
        # [VERIFY] FK present.
        assert response.json["manufacturer_id"] == sample_product.manufacturer_id

    # [TEST][NEGATIVE] Resource not found.
    def test_should_return_404_when_product_not_found(self, client):
        """
        [ARRANGE] No product with ID 999.
        [ACT] GET /api/products/999
        [ASSERT] Returns 404.
        """
        response = client.get("/api/products/999")
        assert response.status_code == 404


# [CLASS] Test POST /api/products (create).
class TestProductPostEndpoint:
    """[WHY] Verify product creation with FK and validation.
    """

    # [TEST][POSITIVE] Standard creation.
    def test_should_create_product_with_valid_data(self, client, sample_manufacturer):
        """
        [ARRANGE] Valid payload with existing manufacturer_id.
        [ACT] POST /api/products
        [ASSERT] Returns 201 with created product including ID.
        
        [WHY] Verify creation works and FK is stored.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "Gadget X",
            "category": "Electronics",
            "price": 199.99,
            "stock_quantity": 100,
            "description": "A great gadget",
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 201
        # [VERIFY] ID auto-generated.
        assert response.json["product_id"] is not None
        assert response.json["product_name"] == "Gadget X"
        # [VERIFY] FK stored.
        assert response.json["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert float(response.json["price"]) == 199.99

    # [TEST][NEGATIVE][VALIDATION] Missing required field.
    def test_should_return_400_when_missing_required_field(self, client, sample_manufacturer):
        """
        [ARRANGE] Payload missing 'price'.
        [ACT] POST /api/products
        [ASSERT] Returns 400 with error message.
        
        [WHY] Validate input validation prevents incomplete data.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "Incomplete",
            "category": "Test",
            "stock_quantity": 50,
            # Missing: price
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        # [VERIFY] Error message helpful.
        assert "price" in response.json["error"]

    # [TEST][NEGATIVE][FK] Invalid manufacturer reference.
    def test_should_return_404_when_manufacturer_not_found(self, client):
        """
        [ARRANGE] Payload with non-existent manufacturer_id=999.
        [ACT] POST /api/products
        [ASSERT] Returns 404.
        
        [WHY] FK constraint: product must link to real manufacturer.
        """
        payload = {
            "manufacturer_id": 999,  # Does not exist.
            "product_name": "Orphan",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": 10,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 404
        assert "error" in response.json
        # [VERIFY] Error explains FK failure.
        assert "manufacturer" in response.json["error"].lower()

    # [TEST][NEGATIVE][VALIDATION] Negative price.
    def test_should_return_400_when_price_is_negative(self, client, sample_manufacturer):
        """
        [ARRANGE] Payload with price=-10.00.
        [ACT] POST /api/products
        [ASSERT] Returns 400.
        
        [WHY] Business rule: price must be non-negative.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "BadPrice",
            "category": "Test",
            "price": -10.00,  # Invalid.
            "stock_quantity": 50,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "price" in response.json["error"].lower()

    # [TEST][NEGATIVE][VALIDATION] Negative stock.
    def test_should_return_400_when_stock_quantity_is_negative(self, client, sample_manufacturer):
        """
        [ARRANGE] Payload with stock_quantity=-5.
        [ACT] POST /api/products
        [ASSERT] Returns 400.
        
        [WHY] Business rule: inventory cannot be negative.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "BadStock",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": -5,  # Invalid.
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "stock_quantity" in response.json["error"].lower()

    # [TEST][NEGATIVE][CONSTRAINT] Duplicate product name per manufacturer.
    def test_should_return_409_when_product_name_duplicate_per_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        [ARRANGE] sample_product already named "TestProduct" under sample_manufacturer.
        [ACT] POST product with same name under same manufacturer.
        [ASSERT] Returns 409 Conflict.
        
        [WHY] Unique constraint: (manufacturer_id, product_name) must be unique.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "TestProduct",  # Duplicate.
            "category": "Different",
            "price": 75.00,
            "stock_quantity": 30,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 409
        assert "error" in response.json

    # [TEST][POSITIVE][BOUNDARY] Same name, different manufacturer allowed.
    def test_should_allow_same_product_name_different_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        [ARRANGE] sample_product is "TestProduct" under sample_manufacturer.
        [ACT] Create new manufacturer, POST product named "TestProduct" under it.
        [ASSERT] Returns 201 (allowed).
        
        [WHY] Unique constraint scoped to manufacturer; same name OK elsewhere.
        """
        # [SETUP] Create second manufacturer.
        second_mfg = {
            "name": "SecondCorp",
            "country": "Mexico",
            "founded_year": 2018,
            "headquarters_city": "Mexico City",
        }
        mfg_response = client.post("/api/manufacturers", json=second_mfg)
        second_mfg_id = mfg_response.json["manufacturer_id"]

        # [ACT] Create product with same name under different manufacturer.
        payload = {
            "manufacturer_id": second_mfg_id,
            "product_name": "TestProduct",  # Same name, OK.
            "category": "Different",
            "price": 100.00,
            "stock_quantity": 50,
        }
        response = client.post("/api/products", json=payload)

        # [VERIFY] Success; different FK allows same name.
        assert response.status_code == 201
        assert response.json["product_name"] == "TestProduct"
        assert response.json["manufacturer_id"] == second_mfg_id


# [CLASS] Test PUT /api/products/{id} (update).
class TestProductPutEndpoint:
    """[WHY] Verify partial updates and FK changes.
    """

    # [TEST][POSITIVE] Partial update.
    def test_should_update_product_fields(self, client, sample_product):
        """
        [ARRANGE] Existing product.
        [ACT] PUT with name, price, stock (not category or description).
        [ASSERT] Those changed; others unchanged.
        """
        product_id = sample_product.product_id
        payload = {
            "product_name": "UpdatedProduct",
            "price": 149.99,
            "stock_quantity": 25,
        }
        response = client.put(f"/api/products/{product_id}", json=payload)

        assert response.status_code == 200
        # [VERIFY] Changed.
        assert response.json["product_name"] == "UpdatedProduct"
        assert float(response.json["price"]) == 149.99
        assert response.json["stock_quantity"] == 25
        # [VERIFY] Untouched.
        assert response.json["category"] == "Test"

    # [TEST][NEGATIVE] Update non-existent.
    def test_should_return_404_when_updating_nonexistent_product(self, client):
        """
        [ARRANGE] No product with ID 999.
        [ACT] PUT /api/products/999
        [ASSERT] Returns 404.
        """
        payload = {"product_name": "NewName"}
        response = client.put("/api/products/999", json=payload)

        assert response.status_code == 404

    # [TEST][NEGATIVE][VALIDATION] Cannot set negative price.
    def test_should_reject_negative_price_on_update(self, client, sample_product):
        """
        [ARRANGE] Existing product with price=99.99.
        [ACT] PUT with price=-50.00.
        [ASSERT] Returns 400.
        
        [WHY] Update validation: business rule enforced on change.
        """
        product_id = sample_product.product_id
        payload = {"price": -50.00}
        response = client.put(f"/api/products/{product_id}", json=payload)

        assert response.status_code == 400
        assert "error" in response.json

    # [TEST][POSITIVE] Reassign to different manufacturer.
    def test_should_allow_moving_product_to_different_manufacturer(
        self, client, sample_product
    ):
        """
        [ARRANGE] Product linked to one manufacturer.
        [ACT] PUT manufacturer_id to different manufacturer.
        [ASSERT] Product now belongs to second manufacturer.
        
        [WHY] FK can be changed; product can move between manufacturers.
        """
        # [SETUP] Create second manufacturer.
        second_mfg = {
            "name": "AnotherCorp",
            "country": "Brazil",
            "founded_year": 2012,
            "headquarters_city": "Rio",
        }
        mfg_response = client.post("/api/manufacturers", json=second_mfg)
        second_mfg_id = mfg_response.json["manufacturer_id"]

        # [ACT] Move product.
        product_id = sample_product.product_id
        payload = {"manufacturer_id": second_mfg_id}
        response = client.put(f"/api/products/{product_id}", json=payload)

        # [VERIFY] FK changed.
        assert response.status_code == 200
        assert response.json["manufacturer_id"] == second_mfg_id


# [CLASS] Test DELETE /api/products/{id}.
class TestProductDeleteEndpoint:
    """[WHY] Verify deletion.
    """

    # [TEST][POSITIVE] Standard deletion.
    def test_should_delete_product(self, client, sample_product):
        """
        [ARRANGE] Existing product.
        [ACT] DELETE /api/products/{id}
        [ASSERT] Returns 200, then GET returns 404.
        """
        product_id = sample_product.product_id
        response = client.delete(f"/api/products/{product_id}")

        # [VERIFY] Deletion response.
        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()

        # [VERIFY] Gone.
        get_response = client.get(f"/api/products/{product_id}")
        assert get_response.status_code == 404

    # [TEST][NEGATIVE] Delete non-existent.
    def test_should_return_404_when_deleting_nonexistent_product(self, client):
        """
        [ARRANGE] No product with ID 999.
        [ACT] DELETE /api/products/999
        [ASSERT] Returns 404.
        """
        response = client.delete("/api/products/999")
        assert response.status_code == 404


# [CLASS] Test one-to-many relationship behavior.
class TestProductManufacturerRelationship:
    """[WHY] Verify cascade delete and FK integrity.
    """

    # [TEST][RELATIONSHIP] Cascade delete products when manufacturer deleted.
    def test_should_cascade_delete_products_when_manufacturer_deleted(
        self, client, sample_product, sample_manufacturer
    ):
        """
        [ARRANGE] Product linked to manufacturer via FK.
        [ACT] DELETE the manufacturer.
        [ASSERT] Product is also deleted (cascade).
        
        [WHY] FK CASCADE rule: deleting master removes all details.
        [EFFECT] Prevents orphaned products; ensures referential integrity.
        """
        product_id = sample_product.product_id
        mfg_id = sample_manufacturer.manufacturer_id

        # [VERIFY] Product exists initially.
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 200

        # [ACT] Delete manufacturer.
        client.delete(f"/api/manufacturers/{mfg_id}")

        # [VERIFY] Product cascaded (also deleted).
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 404

    # [TEST][FK_CONSTRAINT] Invalid FK reference rejected.
    def test_should_reject_product_with_invalid_manufacturer_reference(self, client):
        """
        [ARRANGE] Payload with manufacturer_id=99999 (invalid).
        [ACT] POST /api/products
        [ASSERT] Returns 404.
        
        [WHY] FK constraint: products must link to real manufacturers.
        """
        payload = {
            "manufacturer_id": 99999,  # Invalid.
            "product_name": "Orphan",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": 10,
        }
        response = client.post("/api/products", json=payload)

        # [VERIFY] Rejected.
        assert response.status_code == 404
