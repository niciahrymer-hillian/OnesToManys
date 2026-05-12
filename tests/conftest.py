"""Pytest configuration and shared fixtures for all tests.

Why: Centralizes test setup, database initialization, and Flask app context.
Effect: All test modules can reuse fixtures without duplicating setup code.
"""

import pytest
from app import app, db
from models import Manufacturer, Product


@pytest.fixture
def client():
    """Create a test client with a clean database.
    
    Why: Each test gets a fresh database so tests are independent.
    Effect: No test pollution; tests can run in any order.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_manufacturer(client):
    """Create a sample manufacturer for testing.
    
    Why: Avoid duplicating manufacturer creation in every test.
    Effect: Faster test writing and more readable test names.
    """
    with app.app_context():
        mfg = Manufacturer(
            name="TestCorp",
            country="USA",
            founded_year=2020,
            headquarters_city="Test City",
            is_active=True,
        )
        db.session.add(mfg)
        db.session.commit()
        yield mfg


@pytest.fixture
def sample_product(client, sample_manufacturer):
    """Create a sample product linked to sample_manufacturer.
    
    Why: Test products need a valid manufacturer parent.
    Effect: Reduces boilerplate in product-focused tests.
    """
    with app.app_context():
        product = Product(
            manufacturer_id=sample_manufacturer.manufacturer_id,
            product_name="TestProduct",
            category="Test",
            price=99.99,
            stock_quantity=50,
            description="A test product",
        )
        db.session.add(product)
        db.session.commit()
        yield product
