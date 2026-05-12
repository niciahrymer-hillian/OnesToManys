"""[FILE] models_annotated_cp.py

[WHY]
Defines ORM entities for the one-to-many Manufacturer -> Product domain.

[EFFECT]
API routes can perform CRUD with consistent data constraints and serialization.
"""

# [IMPORT] ORM entry point for Flask applications.
from flask_sqlalchemy import SQLAlchemy


# [FIELD][GLOBAL] Shared SQLAlchemy object bound in app startup.
db = SQLAlchemy()


# [CLASS] Master entity.
class Manufacturer(db.Model):
    """[WHY] Stores top-level manufacturer records.
    [EFFECT] Products can be attached through a parent relationship.
    """

    # [CONSTANT] Explicit table name to match project SQL scripts.
    __tablename__ = "manufacturers"

    # [FIELD][PK]
    manufacturer_id = db.Column(db.Integer, primary_key=True)

    # [FIELD][BUSINESS]
    name = db.Column(db.String(120), nullable=False, unique=True)
    country = db.Column(db.String(80), nullable=False)
    founded_year = db.Column(db.Integer, nullable=False)
    headquarters_city = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # [FIELD][AUDIT]
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    # [RELATIONSHIP] One manufacturer owns many products.
    products = db.relationship(
        "Product",
        back_populates="manufacturer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # [METHOD][SERIALIZATION]
    def to_dict(self):
        """[RETURN] JSON-safe dictionary for API responses."""
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


# [CLASS] Detail entity.
class Product(db.Model):
    """[WHY] Stores product records linked to one manufacturer.
    [EFFECT] Enforces master-detail integrity through foreign keys.
    """

    # [CONSTANT]
    __tablename__ = "products"

    # [FIELD][PK]
    product_id = db.Column(db.Integer, primary_key=True)

    # [FIELD][FK]
    manufacturer_id = db.Column(
        db.Integer,
        db.ForeignKey("manufacturers.manufacturer_id", ondelete="CASCADE"),
        nullable=False,
    )

    # [FIELD][BUSINESS]
    product_name = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)

    # [FIELD][AUDIT]
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

    # [RELATIONSHIP] Many products belong to one manufacturer.
    manufacturer = db.relationship("Manufacturer", back_populates="products")

    # [CONSTRAINT] No duplicate product names within one manufacturer scope.
    __table_args__ = (
        db.UniqueConstraint("manufacturer_id", "product_name", name="uq_product_name_per_mfg"),
    )

    # [METHOD][SERIALIZATION]
    def to_dict(self):
        """[RETURN] JSON-safe dictionary for API responses."""
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
