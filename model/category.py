from app import db

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True, default=None)

    parent = db.relationship(
        'Category',
        remote_side=[id],
        backref=db.backref('children', lazy='dynamic')
    )