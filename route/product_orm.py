from app import app, db
from flask import request
from model import Product

@app.get('/product/list_orm')
def list_orm():
    product = Product.query.all()
    return {
        'products': [
            {'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock}
            for p in product
        ]
    }, 200

@app.get('/product/list-by-id_orm/<int:id>')
def list_by_id_orm(id):
    result = get_product_by_id_orm(id)
    return result, 200

@app.get('/product/list-by-name_orm/<string:name>')
def list_by_name_orm(name):
    result = get_product_by_name_orm(name)
    return result, 200

@app.post('/product/insert_orm')
def insert_orm():
    form = request.get_json()
    if not form:
        return {"error": "No input data provided"}, 400

    if "name" not in form or form["name"] == "":
        return {"error": "Name is required"}, 400

    if "price" not in form:
        return {"error": "Price is required"}, 400

    stock = form.get("stock", 0)

    product = Product(
        name=form.get("name"),
        price=form.get("price"),
        stock=stock
    )
    db.session.add(product)
    db.session.commit()

    return {
        "message": "Product inserted",
    }, 200

def get_product_by_id_orm(id: int) -> dict:
    product = Product.query.get(id)
    if product:
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }
    return {"error": "Product not found"}

def get_product_by_name_orm(name: str) -> dict:
    product = Product.query.filter_by(name=name).first()
    if product:
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }
    return {"error": "Product not found"}

@app.post('/product/delete_orm')
def delete_product_orm():
    form = request.get_json()
    id = form.get("id")
    product = Product.query.get(id)
    if not product:
        return {"error": "Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    return {"message": f"Product with id {id} deleted"}, 200

@app.post('/product/update_orm')
def update_product_orm():
    form = request.get_json()
    id = form.get("id")
    product = Product.query.get(id)
    if not product:
        return {"error": "Product not found"}, 404

    product.name = form.get("name", product.name)
    product.price = form.get("price", product.price)
    product.stock = form.get("stock", product.stock)

    db.session.commit()

    return {
        "message": f"Product with id {id} updated",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock
        }
    }, 200
