
"""
Flask REST API for Manufacturer/Product CRUD and JSON import/export endpoints.

WHY: Implements the project API goals with straightforward, testable routes.
EFFECT: Enables curl and GUI clients to manage master/detail data and move it between files.

Key architectural choices:
- All endpoints are minimal and RESTful for clarity and testability.
- Helper functions (_parse_decimal, _parse_non_negative_int, _error) centralize validation and error handling.
- Schema migration logic (_ensure_product_stats_columns) ensures the DB stays up-to-date without manual resets.
- JSON import/export enables easy backup and reload of all data for demos/testing.
"""

from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from models import Manufacturer, Product, db


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)


with app.app_context():
    db.create_all()



def _ensure_product_stats_columns():
    """
    Add new product statistics columns to older SQLite databases.

    WHY: The local data.db may already exist from an earlier schema version.
    EFFECT: The app keeps running after schema updates without forcing a manual reset.
    """

    with db.engine.connect() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(products)"))
        }
        additions = [
            ("units_sold", "INTEGER NOT NULL DEFAULT 0"),
            ("revenue", "DECIMAL(12,2) NOT NULL DEFAULT 0"),
            ("order_origin", "TEXT NOT NULL DEFAULT 'Online'"),
            ("sales_channel", "TEXT NOT NULL DEFAULT 'Direct'"),
        ]

        for column_name, column_definition in additions:
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE products ADD COLUMN {column_name} {column_definition}")
                )
        connection.commit()


with app.app_context():
    _ensure_product_stats_columns()



def _error(message, status_code=400):
    """
    Return a standardized error response for the API.
    WHY: Ensures all errors are JSON and consistent for frontend consumption.
    """
    return jsonify({"error": message}), status_code



def _parse_decimal(value, field_name):
    """
    Parse and validate a decimal field from input.
    WHY: Centralizes numeric validation for price/revenue fields.
    """
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, _error(f"{field_name} must be a valid number")
    if number < 0:
        return None, _error(f"{field_name} must be non-negative")
    return number, None



def _parse_non_negative_int(value, field_name):
    """
    Parse and validate a non-negative integer field from input.
    WHY: Used for stock, units_sold, and year fields.
    """
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None, _error(f"{field_name} must be an integer")
    if number < 0:
        return None, _error(f"{field_name} must be non-negative")
    return number, None



def _export_payload():
    """
    Export all manufacturers and their products as a JSON-serializable dict.
    WHY: Used for backup, migration, and demo reloads.
    """
    manufacturers = Manufacturer.query.order_by(Manufacturer.manufacturer_id).all()
    return {
        "manufacturers": [
            {
                **manufacturer.to_dict(),
                "products": [product.to_dict() for product in sorted(manufacturer.products, key=lambda item: item.product_id)],
            }
            for manufacturer in manufacturers
        ]
    }



def _load_payload(payload):
    """
    Load manufacturers and products from a JSON payload.
    WHY: Used for restoring a saved state or demo data.
    EFFECT: Wipes existing data and replaces with payload contents.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("manufacturers"), list):
        return _error("Payload must include a manufacturers list")

    # Clear all data before import for a clean slate
    Product.query.delete()
    Manufacturer.query.delete()

    for manufacturer_data in payload["manufacturers"]:
        if not isinstance(manufacturer_data, dict):
            db.session.rollback()
            return _error("Each manufacturer entry must be an object")

        required_manufacturer_fields = ["name", "country", "founded_year", "headquarters_city"]
        missing_manufacturer_fields = [
            field for field in required_manufacturer_fields if field not in manufacturer_data
        ]
        if missing_manufacturer_fields:
            db.session.rollback()
            return _error(
                f"Missing manufacturer fields: {', '.join(missing_manufacturer_fields)}"
            )

        try:
            founded_year = int(manufacturer_data["founded_year"])
        except (TypeError, ValueError):
            db.session.rollback()
            return _error("founded_year must be an integer")

        manufacturer = Manufacturer(
            name=str(manufacturer_data["name"]).strip(),
            country=str(manufacturer_data["country"]).strip(),
            founded_year=founded_year,
            headquarters_city=str(manufacturer_data["headquarters_city"]).strip(),
            is_active=bool(manufacturer_data.get("is_active", True)),
        )
        if manufacturer_data.get("manufacturer_id") is not None:
            manufacturer.manufacturer_id = int(manufacturer_data["manufacturer_id"])

        db.session.add(manufacturer)
        db.session.flush()

        products = manufacturer_data.get("products", [])
        if not isinstance(products, list):
            db.session.rollback()
            return _error("manufacturer products must be a list")

        for product_data in products:
            if not isinstance(product_data, dict):
                db.session.rollback()
                return _error("Each product entry must be an object")

            required_product_fields = ["product_name", "category", "price", "stock_quantity"]
            missing_product_fields = [field for field in required_product_fields if field not in product_data]
            if missing_product_fields:
                db.session.rollback()
                return _error(f"Missing product fields: {', '.join(missing_product_fields)}")

            price, price_error = _parse_decimal(product_data["price"], "price")
            if price_error:
                db.session.rollback()
                return price_error

            stock_quantity, stock_error = _parse_non_negative_int(
                product_data["stock_quantity"], "stock_quantity"
            )
            if stock_error:
                db.session.rollback()
                return stock_error

            product = Product(
                manufacturer_id=manufacturer.manufacturer_id,
                product_name=str(product_data["product_name"]).strip(),
                category=str(product_data["category"]).strip(),
                price=price,
                stock_quantity=stock_quantity,
                units_sold=int(product_data.get("units_sold", 0)),
                revenue=Decimal(str(product_data.get("revenue", 0))),
                order_origin=str(product_data.get("order_origin", "Online")).strip(),
                sales_channel=str(product_data.get("sales_channel", "Direct")).strip(),
                description=product_data.get("description"),
            )
            if product_data.get("product_id") is not None:
                product.product_id = int(product_data["product_id"])

            db.session.add(product)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Import payload violates uniqueness or relationship constraints", 409)

    return None



# Health check endpoint for devops/testing
@app.get("/")
def health_check():
    """Simple health check endpoint."""
    return jsonify({"message": "Manufacturer-Products API is running"})



# List all manufacturers
@app.get("/api/manufacturers")
def get_manufacturers():
    manufacturers = Manufacturer.query.order_by(Manufacturer.manufacturer_id).all()
    return jsonify([m.to_dict() for m in manufacturers])



# Get a single manufacturer by ID
@app.get("/api/manufacturers/<int:manufacturer_id>")
def get_manufacturer(manufacturer_id):
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    return jsonify(manufacturer.to_dict())



# List all products for a manufacturer
@app.get("/api/manufacturers/<int:manufacturer_id>/products")
def get_manufacturer_products(manufacturer_id):
    Manufacturer.query.get_or_404(manufacturer_id)
    products = Product.query.filter_by(manufacturer_id=manufacturer_id).order_by(Product.product_id).all()
    return jsonify([p.to_dict() for p in products])



# Create a new product for a manufacturer
@app.post("/api/manufacturers/<int:manufacturer_id>/products")
def create_manufacturer_product(manufacturer_id):
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    data = request.get_json(silent=True) or {}
    required_fields = ["product_name", "category", "price", "stock_quantity"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return _error(f"Missing required fields: {', '.join(missing)}")

    if "manufacturer_id" in data and int(data["manufacturer_id"]) != manufacturer_id:
        return _error("manufacturer_id must match the route manufacturer_id")

    price, price_error = _parse_decimal(data["price"], "price")
    if price_error:
        return price_error

    stock_quantity, stock_error = _parse_non_negative_int(data["stock_quantity"], "stock_quantity")
    if stock_error:
        return stock_error

    product = Product(
        manufacturer_id=manufacturer.manufacturer_id,
        product_name=str(data["product_name"]).strip(),
        category=str(data["category"]).strip(),
        price=price,
        stock_quantity=stock_quantity,
        units_sold=int(data.get("units_sold", 0)),
        revenue=Decimal(str(data.get("revenue", 0))),
        order_origin=str(data.get("order_origin", "Online")).strip(),
        sales_channel=str(data.get("sales_channel", "Direct")).strip(),
        description=data.get("description"),
    )

    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Product name must be unique per manufacturer", 409)

    return jsonify(product.to_dict()), 201


@app.get("/api/manufacturers/<int:manufacturer_id>/products/<int:product_id>")
def get_manufacturer_product(manufacturer_id, product_id):
    Manufacturer.query.get_or_404(manufacturer_id)
    product = Product.query.filter_by(
        manufacturer_id=manufacturer_id,
        product_id=product_id,
    ).first_or_404()
    return jsonify(product.to_dict())


@app.put("/api/manufacturers/<int:manufacturer_id>/products/<int:product_id>")
def update_manufacturer_product(manufacturer_id, product_id):
    Manufacturer.query.get_or_404(manufacturer_id)
    product = Product.query.filter_by(
        manufacturer_id=manufacturer_id,
        product_id=product_id,
    ).first_or_404()
    data = request.get_json(silent=True) or {}

    if "manufacturer_id" in data and int(data["manufacturer_id"]) != manufacturer_id:
        return _error("manufacturer_id must match the route manufacturer_id")
    if "product_name" in data:
        product.product_name = str(data["product_name"]).strip()
    if "category" in data:
        product.category = str(data["category"]).strip()
    if "price" in data:
        price, price_error = _parse_decimal(data["price"], "price")
        if price_error:
            return price_error
        product.price = price
    if "stock_quantity" in data:
        stock_quantity, stock_error = _parse_non_negative_int(data["stock_quantity"], "stock_quantity")
        if stock_error:
            return stock_error
        product.stock_quantity = stock_quantity
    if "units_sold" in data:
        units_sold, units_error = _parse_non_negative_int(data["units_sold"], "units_sold")
        if units_error:
            return units_error
        product.units_sold = units_sold
    if "revenue" in data:
        revenue, revenue_error = _parse_decimal(data["revenue"], "revenue")
        if revenue_error:
            return revenue_error
        product.revenue = revenue
    if "order_origin" in data:
        product.order_origin = str(data["order_origin"]).strip()
    if "sales_channel" in data:
        product.sales_channel = str(data["sales_channel"]).strip()
    if "description" in data:
        product.description = data["description"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Product name must be unique per manufacturer", 409)

    return jsonify(product.to_dict())


@app.delete("/api/manufacturers/<int:manufacturer_id>/products/<int:product_id>")
def delete_manufacturer_product(manufacturer_id, product_id):
    Manufacturer.query.get_or_404(manufacturer_id)
    product = Product.query.filter_by(
        manufacturer_id=manufacturer_id,
        product_id=product_id,
    ).first_or_404()
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


@app.post("/api/manufacturers")
def create_manufacturer():
    data = request.get_json(silent=True) or {}
    required_fields = ["name", "country", "founded_year", "headquarters_city"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return _error(f"Missing required fields: {', '.join(missing)}")

    try:
        founded_year = int(data["founded_year"])
    except (TypeError, ValueError):
        return _error("founded_year must be an integer")

    manufacturer = Manufacturer(
        name=str(data["name"]).strip(),
        country=str(data["country"]).strip(),
        founded_year=founded_year,
        headquarters_city=str(data["headquarters_city"]).strip(),
        is_active=bool(data.get("is_active", True)),
    )

    db.session.add(manufacturer)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Manufacturer name must be unique", 409)

    return jsonify(manufacturer.to_dict()), 201


@app.put("/api/manufacturers/<int:manufacturer_id>")
def update_manufacturer(manufacturer_id):
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        manufacturer.name = str(data["name"]).strip()
    if "country" in data:
        manufacturer.country = str(data["country"]).strip()
    if "founded_year" in data:
        try:
            manufacturer.founded_year = int(data["founded_year"])
        except (TypeError, ValueError):
            return _error("founded_year must be an integer")
    if "headquarters_city" in data:
        manufacturer.headquarters_city = str(data["headquarters_city"]).strip()
    if "is_active" in data:
        manufacturer.is_active = bool(data["is_active"])

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Manufacturer name must be unique", 409)

    return jsonify(manufacturer.to_dict())


@app.delete("/api/manufacturers/<int:manufacturer_id>")
def delete_manufacturer(manufacturer_id):
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    db.session.delete(manufacturer)
    db.session.commit()
    return jsonify({"message": "Manufacturer deleted"})


@app.get("/api/products")
def get_products():
    products = Product.query.order_by(Product.product_id).all()
    return jsonify([p.to_dict() for p in products])


@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@app.get("/api/export/json")
def export_json():
    return app.response_class(
        response=json.dumps(_export_payload(), indent=2),
        mimetype="application/json",
    )


@app.post("/api/import/json")
def import_json():
    payload = request.get_json(silent=True)
    if payload is None:
        return _error("Request body must be valid JSON")

    load_error = _load_payload(payload)
    if load_error:
        return load_error

    return jsonify(
        {
            "message": "Data imported",
            "manufacturer_count": Manufacturer.query.count(),
            "product_count": Product.query.count(),
        }
    ), 201


@app.post("/api/products")
def create_product():
    data = request.get_json(silent=True) or {}
    required_fields = [
        "manufacturer_id",
        "product_name",
        "category",
        "price",
        "stock_quantity",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return _error(f"Missing required fields: {', '.join(missing)}")

    manufacturer = Manufacturer.query.get(data["manufacturer_id"])
    if not manufacturer:
        return _error("manufacturer_id does not reference an existing manufacturer", 404)

    price, price_error = _parse_decimal(data["price"], "price")
    if price_error:
        return price_error

    stock_quantity, stock_error = _parse_non_negative_int(data["stock_quantity"], "stock_quantity")
    if stock_error:
        return stock_error

    product = Product(
        manufacturer_id=manufacturer.manufacturer_id,
        product_name=str(data["product_name"]).strip(),
        category=str(data["category"]).strip(),
        price=price,
        stock_quantity=stock_quantity,
        units_sold=int(data.get("units_sold", 0)),
        revenue=Decimal(str(data.get("revenue", 0))),
        order_origin=str(data.get("order_origin", "Online")).strip(),
        sales_channel=str(data.get("sales_channel", "Direct")).strip(),
        description=data.get("description"),
    )

    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Product name must be unique per manufacturer", 409)

    return jsonify(product.to_dict()), 201


@app.put("/api/products/<int:product_id>")
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(silent=True) or {}

    if "manufacturer_id" in data:
        manufacturer = Manufacturer.query.get(data["manufacturer_id"])
        if not manufacturer:
            return _error("manufacturer_id does not reference an existing manufacturer", 404)
        product.manufacturer_id = manufacturer.manufacturer_id

    if "product_name" in data:
        product.product_name = str(data["product_name"]).strip()
    if "category" in data:
        product.category = str(data["category"]).strip()
    if "price" in data:
        price, price_error = _parse_decimal(data["price"], "price")
        if price_error:
            return price_error
        product.price = price
    if "stock_quantity" in data:
        stock_quantity, stock_error = _parse_non_negative_int(data["stock_quantity"], "stock_quantity")
        if stock_error:
            return stock_error
        product.stock_quantity = stock_quantity
    if "units_sold" in data:
        units_sold, units_error = _parse_non_negative_int(data["units_sold"], "units_sold")
        if units_error:
            return units_error
        product.units_sold = units_sold
    if "revenue" in data:
        revenue, revenue_error = _parse_decimal(data["revenue"], "revenue")
        if revenue_error:
            return revenue_error
        product.revenue = revenue
    if "order_origin" in data:
        product.order_origin = str(data["order_origin"]).strip()
    if "sales_channel" in data:
        product.sales_channel = str(data["sales_channel"]).strip()
    if "description" in data:
        product.description = data["description"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Product name must be unique per manufacturer", 409)

    return jsonify(product.to_dict())


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    cert_file = Path(os.getenv("FLASK_SSL_CERT", "certs/localhost.pem"))
    key_file = Path(os.getenv("FLASK_SSL_KEY", "certs/localhost-key.pem"))
    ssl_context = (
        (str(cert_file), str(key_file)) if cert_file.exists() and key_file.exists() else None
    )

    app.run(debug=True, host=host, port=port, ssl_context=ssl_context)
