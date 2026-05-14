"""Integration tests for nested manufacturer-product relationship endpoints.

Why: Validates product operations when scoped through a manufacturer route.
Effect: Ensures the one-to-many relationship is enforced through nested HTTP APIs.
"""

from app import db
from models import Manufacturer, Product


class TestManufacturerProductsListEndpoint:
    """Test nested GET endpoints for manufacturer-scoped products."""

    def test_should_return_products_for_specific_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: One manufacturer has one product.
        Act: GET /api/manufacturers/{id}/products
        Assert: Returns only that manufacturer's products.
        """
        response = client.get(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products"
        )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["product_id"] == sample_product.product_id
        assert response.json[0]["manufacturer_id"] == sample_manufacturer.manufacturer_id

    def test_should_return_empty_list_when_manufacturer_has_no_products(
        self, client, sample_manufacturer
    ):
        """
        Arrange: Existing manufacturer with no products.
        Act: GET nested products route.
        Assert: Returns empty list.
        """
        response = client.get(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products"
        )

        assert response.status_code == 200
        assert response.json == []

    def test_should_return_404_when_manufacturer_for_list_is_missing(self, client):
        """
        Arrange: No manufacturer with ID 999.
        Act: GET nested products route.
        Assert: Returns 404.
        """
        response = client.get("/api/manufacturers/999/products")
        assert response.status_code == 404


class TestManufacturerProductsPostEndpoint:
    """Test nested POST endpoint for creating products under a manufacturer."""

    def test_should_create_product_for_specific_manufacturer(self, client, sample_manufacturer):
        """
        Arrange: Existing manufacturer and valid product payload.
        Act: POST /api/manufacturers/{id}/products
        Assert: Returns 201 and binds product to route manufacturer.
        """
        payload = {
            "product_name": "Scoped Product",
            "category": "Scoped",
            "price": 120.50,
            "stock_quantity": 20,
            "description": "Created through nested route",
        }
        response = client.post(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products",
            json=payload,
        )

        assert response.status_code == 201
        assert response.json["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert response.json["product_name"] == "Scoped Product"

    def test_should_return_400_when_body_manufacturer_id_conflicts_with_route(
        self, client, sample_manufacturer
    ):
        """
        Arrange: Route manufacturer_id differs from JSON manufacturer_id.
        Act: POST nested product route.
        Assert: Returns 400 because route context is authoritative.
        """
        payload = {
            "manufacturer_id": sample_manufacturer.manufacturer_id + 1,
            "product_name": "Mismatch Product",
            "category": "Scoped",
            "price": 120.50,
            "stock_quantity": 20,
        }
        response = client.post(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products",
            json=payload,
        )

        assert response.status_code == 400
        assert "manufacturer_id must match" in response.json["error"]

    def test_should_return_404_when_manufacturer_for_create_is_missing(self, client):
        """
        Arrange: No manufacturer with ID 999.
        Act: POST nested product route.
        Assert: Returns 404.
        """
        payload = {
            "product_name": "Missing Parent",
            "category": "Scoped",
            "price": 10.00,
            "stock_quantity": 5,
        }
        response = client.post("/api/manufacturers/999/products", json=payload)

        assert response.status_code == 404


class TestManufacturerProductScopedEndpoints:
    """Test nested GET/PUT/DELETE for one product under one manufacturer."""

    def test_should_return_specific_product_for_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: Product belongs to manufacturer.
        Act: GET nested scoped product route.
        Assert: Returns that product.
        """
        response = client.get(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products/{sample_product.product_id}"
        )

        assert response.status_code == 200
        assert response.json["product_id"] == sample_product.product_id
        assert response.json["manufacturer_id"] == sample_manufacturer.manufacturer_id

    def test_should_return_404_when_product_does_not_belong_to_manufacturer(
        self, client, sample_product
    ):
        """
        Arrange: Product exists under one manufacturer, another manufacturer is created.
        Act: GET nested product route using wrong manufacturer.
        Assert: Returns 404 because scope is wrong.
        """
        other_mfg = {
            "name": "WrongScopeCorp",
            "country": "Canada",
            "founded_year": 2014,
            "headquarters_city": "Toronto",
        }
        response = client.post("/api/manufacturers", json=other_mfg)
        other_mfg_id = response.json["manufacturer_id"]

        scoped_response = client.get(
            f"/api/manufacturers/{other_mfg_id}/products/{sample_product.product_id}"
        )
        assert scoped_response.status_code == 404

    def test_should_update_product_for_specific_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: Existing scoped product.
        Act: PUT nested product route with updated fields.
        Assert: Returns updated product.
        """
        payload = {
            "product_name": "Nested Update",
            "price": 88.25,
            "stock_quantity": 12,
        }
        response = client.put(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products/{sample_product.product_id}",
            json=payload,
        )

        assert response.status_code == 200
        assert response.json["product_name"] == "Nested Update"
        assert float(response.json["price"]) == 88.25
        assert response.json["stock_quantity"] == 12

    def test_should_return_400_when_nested_update_body_conflicts_with_route(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: JSON manufacturer_id conflicts with route manufacturer_id.
        Act: PUT nested scoped product route.
        Assert: Returns 400.
        """
        payload = {"manufacturer_id": sample_manufacturer.manufacturer_id + 1}
        response = client.put(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products/{sample_product.product_id}",
            json=payload,
        )

        assert response.status_code == 400
        assert "manufacturer_id must match" in response.json["error"]

    def test_should_delete_product_for_specific_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: Existing scoped product.
        Act: DELETE nested scoped product route.
        Assert: Returns 200, then scoped GET returns 404.
        """
        delete_response = client.delete(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products/{sample_product.product_id}"
        )

        assert delete_response.status_code == 200
        assert "deleted" in delete_response.json["message"].lower()

        get_response = client.get(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products/{sample_product.product_id}"
        )
        assert get_response.status_code == 404


class TestJsonImportExportEndpoints:
    """Test JSON export/import for the manufacturer-product graph."""

    def test_should_export_manufacturers_with_nested_products(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: Existing manufacturer with one product.
        Act: GET /api/export/json
        Assert: Returns nested manufacturer/product JSON for file export.
        """
        response = client.get("/api/export/json")

        assert response.status_code == 200
        assert response.json["manufacturers"][0]["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert response.json["manufacturers"][0]["products"][0]["product_id"] == sample_product.product_id

    def test_should_import_exported_json_and_restore_database(
        self, client, sample_product, sample_manufacturer
    ):
        """
        Arrange: Existing database state is exported, then cleared.
        Act: POST exported JSON into /api/import/json.
        Assert: Import recreates manufacturers and products from the payload.
        """
        export_response = client.get("/api/export/json")
        payload = export_response.get_json()

        with client.application.app_context():
            Product.query.delete()
            Manufacturer.query.delete()
            db.session.commit()

        import_response = client.post("/api/import/json", json=payload)

        assert import_response.status_code == 201
        assert import_response.json["manufacturer_count"] == 1
        assert import_response.json["product_count"] == 1

        manufacturers_response = client.get("/api/manufacturers")
        products_response = client.get("/api/products")

        assert manufacturers_response.status_code == 200
        assert products_response.status_code == 200
        assert len(manufacturers_response.json) == 1
        assert len(products_response.json) == 1
        assert manufacturers_response.json[0]["name"] == sample_manufacturer.name
        assert products_response.json[0]["product_name"] == sample_product.product_name

    def test_should_return_400_when_import_payload_is_not_expected_shape(self, client):
        """
        Arrange: Invalid JSON body that lacks manufacturers list.
        Act: POST /api/import/json.
        Assert: Returns 400 with a validation error.
        """
        response = client.post("/api/import/json", json={"items": []})

        assert response.status_code == 400
        assert "manufacturers list" in response.json["error"]
