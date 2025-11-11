from app import db
from datetime import datetime, UTC
class Invoice(db.Model):
    __tablename__ = "invoice"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    details = db.relationship('InvoiceDetail', back_populates='invoice')
    user = db.relationship('User', back_populates='invoices')
