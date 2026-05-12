"""Flask REST API for Manufacturer/Product CRUD endpoints.

Why: Implements Phase 1 API goals with straightforward, testable routes.
Effect: Enables curl and GUI clients to manage master/detail data.
"""

from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from models import Manufacturer, Product, db


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)


with app.app_context():
    db.create_all()


def _error(message, status_code=400):
    return jsonify({"error": message}), status_code


def _parse_decimal(value, field_name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, _error(f"{field_name} must be a valid number")
    if number < 0:
        return None, _error(f"{field_name} must be non-negative")
    return number, None


def _parse_non_negative_int(value, field_name):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None, _error(f"{field_name} must be an integer")
    if number < 0:
        return None, _error(f"{field_name} must be non-negative")
    return number, None


@app.get("/")
def health_check():
    return jsonify({"message": "Manufacturer-Products API is running"})


@app.get("/api/manufacturers")
def get_manufacturers():
    manufacturers = Manufacturer.query.order_by(Manufacturer.manufacturer_id).all()
    return jsonify([m.to_dict() for m in manufacturers])


@app.get("/api/manufacturers/<int:manufacturer_id>")
def get_manufacturer(manufacturer_id):
    manufacturer = Manufacturer.query.get_or_404(manufacturer_id)
    return jsonify(manufacturer.to_dict())


@app.get("/api/manufacturers/<int:manufacturer_id>/products")
def get_manufacturer_products(manufacturer_id):
    Manufacturer.query.get_or_404(manufacturer_id)
    products = Product.query.filter_by(manufacturer_id=manufacturer_id).order_by(Product.product_id).all()
    return jsonify([p.to_dict() for p in products])


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
    app.run(debug=True)
