"""Unit tests for Manufacturer and Product models.

Why: Ensures ORM models serialize correctly and enforce constraints.
Effect: Catches data representation bugs before they reach the API.
"""

import pytest
from decimal import Decimal
from app import app, db
from models import Manufacturer, Product


class TestManufacturerModel:
    """Test Manufacturer entity behavior and serialization."""

    def test_should_create_manufacturer_with_valid_data(self, sample_manufacturer):
        """
        Arrange: Sample manufacturer is created by fixture.
        Act: Access the created manufacturer.
        Assert: All fields are correctly set.
        """
        assert sample_manufacturer.manufacturer_id is not None
        assert sample_manufacturer.name == "TestCorp"
        assert sample_manufacturer.country == "USA"
        assert sample_manufacturer.founded_year == 2020
        assert sample_manufacturer.is_active is True

    def test_should_serialize_manufacturer_to_dict(self, sample_manufacturer):
        """
        Why: API responses use to_dict() for JSON serialization.
        Assert: Dictionary has all required fields and correct types.
        """
        result = sample_manufacturer.to_dict()

        assert result["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert result["name"] == "TestCorp"
        assert result["country"] == "USA"
        assert result["founded_year"] == 2020
        assert result["is_active"] is True
        assert "created_at" in result
        assert "updated_at" in result

    def test_should_enforce_unique_manufacturer_name(self, sample_manufacturer):
        """
        Why: Business rule: no two manufacturers can share the same name.
        Act: Attempt to create a second manufacturer with duplicate name.
        Assert: Database integrity error is raised.
        """
        with app.app_context():
            duplicate = Manufacturer(
                name="TestCorp",  # Same as sample_manufacturer
                country="Canada",
                founded_year=2021,
                headquarters_city="Other City",
            )
            db.session.add(duplicate)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_should_have_empty_products_list_initially(self, sample_manufacturer):
        """
        Why: Relationship integrity: new manufacturers have no products.
        Assert: products relationship is empty.
        """
        assert len(sample_manufacturer.products) == 0

    def test_should_update_manufacturer_timestamps(self, sample_manufacturer):
        """
        Why: Audit trail: created_at and updated_at track record lifecycle.
        Act: Modify a manufacturer.
        Assert: updated_at changes but created_at stays constant.
        """
        original_created_at = sample_manufacturer.created_at

        with app.app_context():
            sample_manufacturer.is_active = False
            db.session.commit()

            assert sample_manufacturer.created_at == original_created_at
            assert sample_manufacturer.updated_at >= original_created_at


class TestProductModel:
    """Test Product entity behavior and serialization."""

    def test_should_create_product_with_valid_data(self, sample_product):
        """
        Arrange: Sample product is created by fixture.
        Act: Access the created product.
        Assert: All fields are correctly set.
        """
        assert sample_product.product_id is not None
        assert sample_product.product_name == "TestProduct"
        assert sample_product.category == "Test"
        assert sample_product.price == Decimal("99.99")
        assert sample_product.stock_quantity == 50

    def test_should_serialize_product_to_dict(self, sample_product):
        """
        Why: API responses use to_dict() for JSON serialization.
        Assert: Dictionary has all required fields and correct types.
        """
        result = sample_product.to_dict()

        assert result["product_id"] == sample_product.product_id
        assert result["manufacturer_id"] == sample_product.manufacturer_id
        assert result["product_name"] == "TestProduct"
        assert result["category"] == "Test"
        assert float(result["price"]) == 99.99
        assert result["stock_quantity"] == 50
        assert "created_at" in result
        assert "updated_at" in result

    def test_should_link_product_to_manufacturer(self, sample_product, sample_manufacturer):
        """
        Why: Relationship integrity: products must belong to a manufacturer.
        Assert: Product.manufacturer references the correct parent.
        """
        assert sample_product.manufacturer_id == sample_manufacturer.manufacturer_id
        assert sample_product.manufacturer.manufacturer_id == sample_manufacturer.manufacturer_id
        assert sample_product.manufacturer.name == sample_manufacturer.name

    def test_should_enforce_unique_product_name_per_manufacturer(
        self, sample_product, sample_manufacturer
    ):
        """
        Why: Business rule: no duplicate product names within one manufacturer.
        Act: Create a second product with same name under same manufacturer.
        Assert: Integrity error is raised.
        """
        with app.app_context():
            duplicate = Product(
                manufacturer_id=sample_manufacturer.manufacturer_id,
                product_name="TestProduct",  # Same as sample_product
                category="Different",
                price=Decimal("50.00"),
                stock_quantity=100,
            )
            db.session.add(duplicate)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_should_allow_same_product_name_different_manufacturer(
        self, sample_product, sample_manufacturer
    ):
        """
        Why: Unique constraint is per manufacturer, not global.
        Act: Create a product with same name under a different manufacturer.
        Assert: This is allowed and succeeds.
        """
        with app.app_context():
            other_mfg = Manufacturer(
                name="OtherCorp",
                country="UK",
                founded_year=2019,
                headquarters_city="London",
            )
            db.session.add(other_mfg)
            db.session.flush()

            other_product = Product(
                manufacturer_id=other_mfg.manufacturer_id,
                product_name="TestProduct",  # Same as sample_product
                category="Different",
                price=Decimal("75.00"),
                stock_quantity=75,
            )
            db.session.add(other_product)
            db.session.commit()

            assert other_product.product_id is not None
            assert other_product.manufacturer_id != sample_product.manufacturer_id

    def test_should_update_product_timestamps(self, sample_product):
        """
        Why: Audit trail: track when product was last modified.
        Act: Modify a product.
        Assert: updated_at changes but created_at stays constant.
        """
        original_created_at = sample_product.created_at

        with app.app_context():
            sample_product.stock_quantity = 25
            db.session.commit()

            assert sample_product.created_at == original_created_at
            assert sample_product.updated_at >= original_created_at
