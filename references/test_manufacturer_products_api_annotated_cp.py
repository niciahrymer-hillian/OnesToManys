"""[FILE] test_manufacturer_products_api_annotated_cp.py

[WHY]
Integration tests for nested manufacturer-product endpoints validate one-to-many behavior through route scoping.

[EFFECT]
These tests prove products can be managed inside manufacturer context without losing relationship integrity.
"""


# [CLASS] Test GET /api/manufacturers/{id}/products.
class TestManufacturerProductsListEndpoint:
    """[WHY] Verify list retrieval inside manufacturer scope.
    """

    def test_should_return_products_for_specific_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        [ARRANGE] One manufacturer has one product.
        [ACT] GET nested manufacturer products route.
        [ASSERT] Returns only that manufacturer's products.
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
        [ARRANGE] Existing manufacturer with no products.
        [ACT] GET nested products route.
        [ASSERT] Returns empty list.
        
        [WHY] Empty-state behavior should still preserve relationship context.
        """
        response = client.get(
            f"/api/manufacturers/{sample_manufacturer.manufacturer_id}/products"
        )

        assert response.status_code == 200
        assert response.json == []

    def test_should_return_404_when_manufacturer_for_list_is_missing(self, client):
        """
        [ARRANGE] No manufacturer with ID 999.
        [ACT] GET nested products route.
        [ASSERT] Returns 404.
        """
        response = client.get("/api/manufacturers/999/products")
        assert response.status_code == 404


# [CLASS] Test POST /api/manufacturers/{id}/products.
class TestManufacturerProductsPostEndpoint:
    """[WHY] Verify nested creation binds products to route manufacturer.
    """

    def test_should_create_product_for_specific_manufacturer(self, client, sample_manufacturer):
        """
        [ARRANGE] Existing manufacturer and valid product payload.
        [ACT] POST nested product route.
        [ASSERT] Returns 201 and binds product to route manufacturer.
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
        [ARRANGE] Route manufacturer_id differs from JSON manufacturer_id.
        [ACT] POST nested product route.
        [ASSERT] Returns 400.
        
        [WHY] The route context is authoritative for parent ownership.
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
        [ARRANGE] No manufacturer with ID 999.
        [ACT] POST nested product route.
        [ASSERT] Returns 404.
        """
        payload = {
            "product_name": "Missing Parent",
            "category": "Scoped",
            "price": 10.00,
            "stock_quantity": 5,
        }
        response = client.post("/api/manufacturers/999/products", json=payload)

        assert response.status_code == 404


# [CLASS] Test scoped nested detail/update/delete endpoints.
class TestManufacturerProductScopedEndpoints:
    """[WHY] Verify nested detail routes enforce parent-child scope.
    """

    def test_should_return_specific_product_for_manufacturer(
        self, client, sample_product, sample_manufacturer
    ):
        """
        [ARRANGE] Product belongs to manufacturer.
        [ACT] GET nested scoped product route.
        [ASSERT] Returns that product.
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
        [ARRANGE] Product exists under one manufacturer, another manufacturer is created.
        [ACT] GET nested route using wrong manufacturer.
        [ASSERT] Returns 404.
        
        [WHY] Nested routes should not leak products across parent boundaries.
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
        [ARRANGE] Existing scoped product.
        [ACT] PUT nested product route with updated fields.
        [ASSERT] Returns updated product.
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
        [ARRANGE] JSON manufacturer_id conflicts with route manufacturer_id.
        [ACT] PUT nested scoped product route.
        [ASSERT] Returns 400.
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
        [ARRANGE] Existing scoped product.
        [ACT] DELETE nested scoped product route.
        [ASSERT] Returns 200, then scoped GET returns 404.
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
