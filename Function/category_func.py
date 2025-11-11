from app import db
from sqlalchemy import text
from model.category import Category
from model.product import Product
from flask import request

def category_listing():
    sql = text("SELECT * FROM category")
    result = db.session.execute(sql)
    categories = [
        {
            'id': row.id,
            'category_name': row.category_name,
            'parent_id': row.parent_id
        }
        for row in result
    ]
    return {"categories": categories}, 200

def get_category_by_id(id: int) -> dict:
    sql = text("SELECT id, category_name, parent_id FROM category WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()

    if result:
        return {
            'id': result.id,
            'category_name': result.category_name,
            'parent_id': result.parent_id
        }

    return {"error": "Category not found"}

def category_create():
    form = request.get_json(silent=True) or request.form
    category_name = form.get('category_name')
    parent_id = form.get('parent_id')

    if not form:
        return {"error": "No input provided"}, 400
    if form.get('parent_id') and not form.get('category_name'):
        return {"error": "Please fill all required fields"}, 400


    if not parent_id or parent_id in ["", "null", "None"]:
        parent_id = None
    else:
        try:
            parent_id = int(parent_id)
        except ValueError:
            return {"error": "Invalid parent_id"}, 400

    existing_category = Category.query.filter_by(category_name=category_name).first()
    if existing_category:
        return {"error": "Category already exists"}, 400
    category = Category(
        category_name=category_name,
        parent_id=parent_id
    )
    db.session.add(category)
    db.session.commit()

    return {
        "message": "Category Created",
        "category": get_category_by_id(category.id)
    }, 201

def category_delete():
    form = request.get_json(silent=True) or request.form
    if not form or not form.get("id"):
        return {"error": "No Category id provided"}, 400

    category_id = form.get("id")
    category = Category.query.get(category_id)
    if not category:
        return {"error": "Category not found"}, 404

    linked_product = Product.query.filter_by(category_id=category_id).first()
    if linked_product:
        return {
            "error": "Cannot delete this Category because it is linked to existing Product."
        }, 400

    try:
        db.session.delete(category)
        db.session.commit()
        return {"message": f"Category with id {category_id} deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def category_update():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400

    id = form.get("id")
    category_name = form.get("category_name")
    parent_id = form.get("parent_id")

    if not id:
        return {"error": "No id provided"}, 400
    if not category_name:
        return {"error": "No category name provided"}, 400

    category = Category.query.get(id)
    if not category:
        return {"error": "Category not found"}, 404

    if not parent_id or parent_id in ["", "null", "None"]:
        parent_id = None
    else:
        try:
            parent_id = int(parent_id)
        except ValueError:
            return {"error": "Invalid parent_id"}, 400

    existing_category = Category.query.filter(Category.category_name == category_name,Category.id != id).first()
    if existing_category:
        return {"error": "Category name already exists"}, 400

    if parent_id is not None and int(parent_id) == int(id):
        return {"error": "A category cannot be its own parent"}, 400

    category.category_name = category_name
    category.parent_id = parent_id
    db.session.commit()

    return {
        "message": f"Category with id {id} updated",
        "category": get_category_by_id(category.id)
    }, 200