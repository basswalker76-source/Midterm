from sqlalchemy.orm import relationship

from app import db
class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True)

    invoice_details = db.relationship('InvoiceDetail', back_populates='product')