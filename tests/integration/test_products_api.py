"""Integration tests for Product API endpoints.

Why: Ensures all product CRUD operations work and respect manufacturer relationships.
Effect: Validates end-to-end product lifecycle and foreign key integrity.
"""

import json
import pytest
from decimal import Decimal


class TestProductGetEndpoints:
    """Test GET endpoints for products."""

    def test_should_return_empty_list_when_no_products_exist(self, client):
        """
        Arrange: Fresh database with no products.
        Act: GET /api/products
        Assert: Returns empty JSON array with 200 status.
        """
        response = client.get("/api/products")
        assert response.status_code == 200
        assert response.json == []

    def test_should_return_all_products(self, client, sample_product):
        """
        Arrange: One sample product exists.
        Act: GET /api/products
        Assert: Returns array with one product object.
        """
        response = client.get("/api/products")
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["product_name"] == "TestProduct"

    def test_should_return_single_product_by_id(self, client, sample_product):
        """
        Arrange: One sample product exists.
        Act: GET /api/products/{id}
        Assert: Returns the product object with correct fields.
        """
        product_id = sample_product.product_id
        response = client.get(f"/api/products/{product_id}")

        assert response.status_code == 200
        assert response.json["product_id"] == product_id
        assert response.json["product_name"] == "TestProduct"
        assert response.json["manufacturer_id"] == sample_product.manufacturer_id

    def test_should_return_404_when_product_not_found(self, client):
        """
        Arrange: No product with ID 999 exists.
        Act: GET /api/products/999
        Assert: Returns 404 Not Found.
        """
        response = client.get("/api/products/999")
        assert response.status_code == 404


class TestProductPostEndpoint:
    """Test POST endpoint for creating products."""

    def test_should_create_product_with_valid_data(self, client, sample_manufacturer):
        """
        Arrange: Valid product JSON with existing manufacturer ID.
        Act: POST /api/products
        Assert: Returns 201 with created product including ID.
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
        assert response.json["product_id"] is not None
        assert response.json["product_name"] == "Gadget X"
        assert response.json["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert float(response.json["price"]) == 199.99

    def test_should_return_400_when_missing_required_field(self, client, sample_manufacturer):
        """
        Boundary case: Missing required field 'price'.
        Act: POST without price.
        Assert: Returns 400 with error message.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "Incomplete",
            "category": "Test",
            "stock_quantity": 50,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "price" in response.json["error"]

    def test_should_return_404_when_manufacturer_not_found(self, client):
        """
        Negative scenario: Product references non-existent manufacturer.
        Act: POST with invalid manufacturer_id.
        Assert: Returns 404.
        """
        payload = {
            "manufacturer_id": 999,  # Does not exist
            "product_name": "Orphan",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": 10,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 404
        assert "error" in response.json
        assert "manufacturer" in response.json["error"].lower()

    def test_should_return_400_when_price_is_negative(self, client, sample_manufacturer):
        """
        Boundary case: Negative price is invalid.
        Act: POST with negative price.
        Assert: Returns 400 with validation error.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "BadPrice",
            "category": "Test",
            "price": -10.00,
            "stock_quantity": 50,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "price" in response.json["error"].lower()

    def test_should_return_400_when_stock_quantity_is_negative(self, client, sample_manufacturer):
        """
        Boundary case: Negative stock quantity is invalid.
        Act: POST with negative stock_quantity.
        Assert: Returns 400 with validation error.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "BadStock",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": -5,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 400
        assert "error" in response.json
        assert "stock_quantity" in response.json["error"].lower()

    def test_should_return_409_when_product_name_duplicate_per_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Negative scenario: Duplicate product name within one manufacturer.
        Act: POST with same name under same manufacturer.
        Assert: Returns 409 Conflict.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id,
            "product_name": "TestProduct",  # Duplicate
            "category": "Different",
            "price": 75.00,
            "stock_quantity": 30,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 409
        assert "error" in response.json

    def test_should_allow_same_product_name_different_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Positive scenario: Same product name allowed under different manufacturer.
        Arrange: Create second manufacturer.
        Act: POST product with same name as sample_product but different manufacturer.
        Assert: Returns 201 (success).
        """
        # Create a second manufacturer
        second_mfg = {
            "name": "SecondCorp",
            "country": "Mexico",
            "founded_year": 2018,
            "headquarters_city": "Mexico City",
        }
        mfg_response = client.post("/api/manufacturers", json=second_mfg)
        second_mfg_id = mfg_response.json["manufacturer_id"]

        # Create product with same name under second manufacturer
        payload = {
            "manufacturer_id": second_mfg_id,
            "product_name": "TestProduct",  # Same as sample_product
            "category": "Different",
            "price": 100.00,
            "stock_quantity": 50,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 201
        assert response.json["product_name"] == "TestProduct"
        assert response.json["manufacturer_id"] == second_mfg_id


class TestProductPutEndpoint:
    """Test PUT endpoint for updating products."""

    def test_should_update_product_fields(self, client, sample_product):
        """
        Arrange: Existing product with sample data.
        Act: PUT with updated fields.
        Assert: Returns updated product.
        """
        product_id = sample_product.product_id
        payload = {
            "product_name": "UpdatedProduct",
            "price": 149.99,
            "stock_quantity": 25,
        }
        response = client.put(f"/api/products/{product_id}", json=payload)

        assert response.status_code == 200
        assert response.json["product_name"] == "UpdatedProduct"
        assert float(response.json["price"]) == 149.99
        assert response.json["stock_quantity"] == 25
        assert response.json["category"] == "Test"  # Unchanged

    def test_should_return_404_when_updating_nonexistent_product(self, client):
        """
        Negative scenario: Update non-existent product.
        Act: PUT /api/products/999
        Assert: Returns 404.
        """
        payload = {"product_name": "NewName"}
        response = client.put("/api/products/999", json=payload)

        assert response.status_code == 404

    def test_should_reject_negative_price_on_update(self, client, sample_product):
        """
        Boundary case: Cannot set price to negative on update.
        Act: PUT with negative price.
        Assert: Returns 400 with validation error.
        """
        product_id = sample_product.product_id
        payload = {"price": -50.00}
        response = client.put(f"/api/products/{product_id}", json=payload)

        assert response.status_code == 400
        assert "error" in response.json

    def test_should_allow_moving_product_to_different_manufacturer(
        self, client, sample_product
    ):
        """
        Positive scenario: Reassign product to different manufacturer.
        Arrange: Create second manufacturer.
        Act: PUT product to update manufacturer_id.
        Assert: Product now belongs to second manufacturer.
        """
        # Create second manufacturer
        second_mfg = {
            "name": "AnotherCorp",
            "country": "Brazil",
            "founded_year": 2012,
            "headquarters_city": "Rio",
        }
        mfg_response = client.post("/api/manufacturers", json=second_mfg)
        second_mfg_id = mfg_response.json["manufacturer_id"]

        # Move product to second manufacturer
        product_id = sample_product.product_id
        payload = {"manufacturer_id": second_mfg_id}
        response = client.put(f"/api/products/{product_id}", json=payload)

        assert response.status_code == 200
        assert response.json["manufacturer_id"] == second_mfg_id


class TestProductDeleteEndpoint:
    """Test DELETE endpoint for products."""

    def test_should_delete_product(self, client, sample_product):
        """
        Arrange: Existing product.
        Act: DELETE /api/products/{id}
        Assert: Returns 200 with success message, then GET returns 404.
        """
        product_id = sample_product.product_id
        response = client.delete(f"/api/products/{product_id}")

        assert response.status_code == 200
        assert "deleted" in response.json["message"].lower()

        # Verify deletion
        get_response = client.get(f"/api/products/{product_id}")
        assert get_response.status_code == 404

    def test_should_return_404_when_deleting_nonexistent_product(self, client):
        """
        Negative scenario: Delete non-existent product.
        Act: DELETE /api/products/999
        Assert: Returns 404.
        """
        response = client.delete("/api/products/999")
        assert response.status_code == 404


class TestProductManufacturerRelationship:
    """Test one-to-many relationship behavior."""

    def test_should_cascade_delete_products_when_manufacturer_deleted(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Why: Foreign key cascade delete ensures data integrity.
        Arrange: Create product linked to manufacturer.
        Act: DELETE the manufacturer.
        Assert: Product is also deleted (cascade).
        """
        product_id = sample_product.product_id
        mfg_id = sample_manufacturer.manufacturer_id

        # Verify product exists
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 200

        # Delete manufacturer
        client.delete(f"/api/manufacturers/{mfg_id}")

        # Verify product is also deleted (cascade)
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 404

    def test_should_reject_product_with_invalid_manufacturer_reference(self, client):
        """
        Why: Foreign key constraint prevents orphaned products.
        Act: Attempt to create product with non-existent manufacturer.
        Assert: Returns 404.
        """
        payload = {
            "manufacturer_id": 99999,  # Invalid ID
            "product_name": "Orphan",
            "category": "Test",
            "price": 50.00,
            "stock_quantity": 10,
        }
        response = client.post("/api/products", json=payload)

        assert response.status_code == 404
