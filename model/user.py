from app import db
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    email = db.Column(db.String(100), unique=True, nullable=True, default=None)
    profile = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(100), nullable=False, default=None)

    invoices = db.relationship('Invoice', back_populates='user')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)