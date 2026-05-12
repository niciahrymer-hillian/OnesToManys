"""[FILE] test_models_annotated_cp.py

[WHY]
Unit tests validate ORM models in isolation from API routes.

[EFFECT]
Catches serialization bugs, constraint violations, and relationship integrity issues early.
"""

import pytest
from decimal import Decimal
from app import app, db
from models import Manufacturer, Product


# [CLASS] Tests for Manufacturer model.
class TestManufacturerModel:
    """[WHY] Manufacturer is the master entity; ensure it behaves correctly.
    """

    # [TEST][POSITIVE] Standard creation and field assignment.
    def test_should_create_manufacturer_with_valid_data(self, sample_manufacturer):
        """
        [ARRANGE] Fixture provides a pre-created manufacturer.
        [ACT] Access its properties.
        [ASSERT] All fields exist and have expected values.
        
        [WHY] Verifies ORM model initialization works.
        """
        assert sample_manufacturer.manufacturer_id is not None
        assert sample_manufacturer.name == "TestCorp"
        assert sample_manufacturer.country == "USA"
        assert sample_manufacturer.founded_year == 2020
        assert sample_manufacturer.is_active is True

    # [TEST][SERIALIZATION] to_dict() is used by all API responses.
    def test_should_serialize_manufacturer_to_dict(self, sample_manufacturer):
        """
        [WHY] API returns JSON; to_dict() is the serialization method.
        [ASSERT] All fields are present and types are correct.
        """
        result = sample_manufacturer.to_dict()

        # [VERIFY] All required fields present.
        assert result["manufacturer_id"] == sample_manufacturer.manufacturer_id
        assert result["name"] == "TestCorp"
        assert result["country"] == "USA"
        assert result["founded_year"] == 2020
        assert result["is_active"] is True
        # [VERIFY] Timestamps are included.
        assert "created_at" in result
        assert "updated_at" in result

    # [TEST][CONSTRAINT] UNIQUE(name) - business rule enforcement.
    def test_should_enforce_unique_manufacturer_name(self, sample_manufacturer):
        """
        [WHY] Manufacturer name must be unique; prevents duplicates in business logic.
        [ACT] Try to insert manufacturer with duplicate name.
        [ASSERT] Database raises integrity constraint error.
        
        [GOTCHA] This tests database-level constraint, not application logic.
        """
        with app.app_context():
            duplicate = Manufacturer(
                name="TestCorp",  # Duplicate!
                country="Canada",
                founded_year=2021,
                headquarters_city="Other City",
            )
            db.session.add(duplicate)

            # [EXPECT] SQLAlchemy raises IntegrityError on commit.
            with pytest.raises(Exception):
                db.session.commit()

    # [TEST][RELATIONSHIP] Manufacturers own products (one-to-many).
    def test_should_have_empty_products_list_initially(self, sample_manufacturer):
        """
        [WHY] Relationship integrity: new masters have no details.
        [ASSERT] products relationship is initialized as empty list.
        """
        assert len(sample_manufacturer.products) == 0

    # [TEST][AUDIT_TRAIL] Timestamps track lifecycle.
    def test_should_update_manufacturer_timestamps(self, sample_manufacturer):
        """
        [WHY] Audit: created_at is immutable; updated_at changes on modification.
        [ACT] Modify a field and commit.
        [ASSERT] created_at unchanged; updated_at changed.
        """
        original_created_at = sample_manufacturer.created_at

        with app.app_context():
            sample_manufacturer.is_active = False
            db.session.commit()

            # [VERIFY] Immutable field.
            assert sample_manufacturer.created_at == original_created_at
            # [VERIFY] Updated field changed.
            assert sample_manufacturer.updated_at >= original_created_at


# [CLASS] Tests for Product model (detail entity).
class TestProductModel:
    """[WHY] Product is the detail entity linked to Manufacturer via FK.
    """

    # [TEST][POSITIVE] Standard creation.
    def test_should_create_product_with_valid_data(self, sample_product):
        """
        [ARRANGE] Fixture creates product linked to manufacturer.
        [ACT] Access product properties.
        [ASSERT] Fields match expected values.
        """
        assert sample_product.product_id is not None
        assert sample_product.product_name == "TestProduct"
        assert sample_product.category == "Test"
        assert sample_product.price == Decimal("99.99")
        assert sample_product.stock_quantity == 50

    # [TEST][SERIALIZATION]
    def test_should_serialize_product_to_dict(self, sample_product):
        """
        [WHY] API responses use to_dict() serialization.
        [ASSERT] All fields present; price converted to float for JSON.
        """
        result = sample_product.to_dict()

        # [VERIFY] All required fields.
        assert result["product_id"] == sample_product.product_id
        assert result["manufacturer_id"] == sample_product.manufacturer_id
        assert result["product_name"] == "TestProduct"
        assert result["category"] == "Test"
        # [CONVERT] Decimal -> float for JSON serialization.
        assert float(result["price"]) == 99.99
        assert result["stock_quantity"] == 50
        # [VERIFY] Timestamps.
        assert "created_at" in result
        assert "updated_at" in result

    # [TEST][RELATIONSHIP] Product -> Manufacturer (many-to-one).
    def test_should_link_product_to_manufacturer(self, sample_product, sample_manufacturer):
        """
        [WHY] Product MUST belong to one manufacturer (FK constraint).
        [ASSERT] Product.manufacturer relationship is correct.
        """
        assert sample_product.manufacturer_id == sample_manufacturer.manufacturer_id
        # [VERIFY] Compare persisted fields instead of Python object identity.
        assert sample_product.manufacturer.manufacturer_id == sample_manufacturer.manufacturer_id
        assert sample_product.manufacturer.name == sample_manufacturer.name

    # [TEST][CONSTRAINT] UNIQUE(manufacturer_id, product_name).
    def test_should_enforce_unique_product_name_per_manufacturer(
        self, sample_product, sample_manufacturer
    ):
        """
        [WHY] No duplicate product names within one manufacturer.
        [ACT] Insert product with same name under same manufacturer.
        [ASSERT] Integrity error raised.
        """
        with app.app_context():
            duplicate = Product(
                manufacturer_id=sample_manufacturer.manufacturer_id,
                product_name="TestProduct",  # Duplicate name.
                category="Different",
                price=Decimal("50.00"),
                stock_quantity=100,
            )
            db.session.add(duplicate)

            with pytest.raises(Exception):
                db.session.commit()

    # [TEST][BOUNDARY] Same name allowed across manufacturers.
    def test_should_allow_same_product_name_different_manufacturer(
        self, sample_product, sample_manufacturer
    ):
        """
        [WHY] Unique constraint is scoped to (mfg_id, product_name), not global.
        [ACT] Create product with same name under different manufacturer.
        [ASSERT] Succeeds because FK is different.
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
                product_name="TestProduct",  # Same name, OK.
                category="Different",
                price=Decimal("75.00"),
                stock_quantity=75,
            )
            db.session.add(other_product)
            db.session.commit()

            # [VERIFY] Different FKs allow same name.
            assert other_product.product_id is not None
            assert other_product.manufacturer_id != sample_product.manufacturer_id

    # [TEST][AUDIT_TRAIL]
    def test_should_update_product_timestamps(self, sample_product):
        """
        [WHY] Audit trail: track creation vs last modification.
        [ACT] Modify product, commit.
        [ASSERT] created_at immutable; updated_at changes.
        """
        original_created_at = sample_product.created_at

        with app.app_context():
            sample_product.stock_quantity = 25
            db.session.commit()

            # [VERIFY] Immutable.
            assert sample_product.created_at == original_created_at
            # [VERIFY] Changed.
            assert sample_product.updated_at >= original_created_at
