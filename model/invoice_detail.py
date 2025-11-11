from app import db
class InvoiceDetail(db.Model):
    __tablename__ = "invoice_detail"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship('Product', back_populates='invoice_details')
    invoice = db.relationship('Invoice', back_populates='details')
