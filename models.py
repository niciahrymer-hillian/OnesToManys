"""Data models for the Manufacturer (master) and Product (detail) domain.

Why: Centralizes the relational structure in one place so API handlers stay simple.
Effect: The API can rely on consistent ORM models for CRUD operations.
"""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Manufacturer(db.Model):
    """Master entity that can own many products.

    Why: Represents the top-level business object for the one-to-many relationship.
    Effect: Product records can be grouped, queried, and managed by manufacturer.
    """

    __tablename__ = "manufacturers"

    manufacturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    country = db.Column(db.String(80), nullable=False)
    founded_year = db.Column(db.Integer, nullable=False)
    headquarters_city = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    products = db.relationship(
        "Product",
        back_populates="manufacturer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        """Serialize model for JSON responses."""
        return {
            "manufacturer_id": self.manufacturer_id,
            "name": self.name,
            "country": self.country,
            "founded_year": self.founded_year,
            "headquarters_city": self.headquarters_city,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Product(db.Model):
    """Detail entity that belongs to exactly one manufacturer.

    Why: Captures product data while enforcing parent-child integrity.
    Effect: Each product remains traceable to one manufacturer.
    """

    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    manufacturer_id = db.Column(
        db.Integer,
        db.ForeignKey("manufacturers.manufacturer_id", ondelete="CASCADE"),
        nullable=False,
    )
    product_name = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    manufacturer = db.relationship("Manufacturer", back_populates="products")

    __table_args__ = (
        db.UniqueConstraint("manufacturer_id", "product_name", name="uq_product_name_per_mfg"),
    )

    def to_dict(self):
        """Serialize model for JSON responses."""
        return {
            "product_id": self.product_id,
            "manufacturer_id": self.manufacturer_id,
            "product_name": self.product_name,
            "category": self.category,
            "price": float(self.price),
            "stock_quantity": self.stock_quantity,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
