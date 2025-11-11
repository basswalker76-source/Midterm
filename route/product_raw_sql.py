from app import app, db
from sqlalchemy import text
from flask import request

@app.get('/product/list_sql')
def list_sql():
    sql = text("""SELECT * FROM product""")
    result = db.session.execute(sql).fetchall()
    rows = [dict(row._mapping) for row in result]
    return rows, 200

@app.get('/product/list-by-id_sql/<int:id>')
def list_by_id_sql(id):
    result = get_product_by_id_sql(id)
    return result
@app.get('/product/list-by-name_sql/<string:name>')
def list_by_name_sql(name):
    result = get_product_by_name_sql(name)
    return result

@app.post('/product/insert_sql')
def insert_sql():
    form = request.get_json()
    if not form:
        return {"error": "No input data provided"}, 400
    if not form.get('name'):
        return {"error": "Name is Required"}, 400
    if not form.get('price'):
        return {"error": "Price is Required"}, 400

    name = form.get('name')
    price = form.get('price')
    stock = form.get('stock')
    sql = text("""Insert into product (name, price, stock) values (:name, :price, :stock)""")
    result = db.session.execute(sql,
                                {
                                    'name': name,
                                    'price': price,
                                    'stock': stock
                                 })
    db.session.commit()
    return {"message": "Product inserted", "product": get_product_by_id_sql(result.lastrowid)}, 200

def get_product_by_id_sql(id: int) -> dict:
    sql = text("""SELECT * FROM product WHERE id = :id""")
    result = db.session.execute(sql,{'id': id}).fetchone()
    if result:
        return dict(result._mapping)
    return {"error": "Product not found"}

def get_product_by_name_sql(name: str) -> dict:
    sql = text("""SELECT * FROM product WHERE name = :name""")
    result = db.session.execute(sql,{'name': name}).fetchone()
    if result:
        return dict(result._mapping)
    return {"error": "Product not found"}

@app.post('/product/delete_sql')
def delete_sql():
    form = request.get_json()
    if not form.get('id'):
        return {"error": "ID is Required"}, 400
    is_exiting = get_product_by_id_sql(form.get('id'))
    if is_exiting.get('error'):
        return {"error": "Product ID is not found"}, 400

    id = form.get('id')
    sql = text("""Delete from product where id = :id""")
    result = db.session.execute(sql,
                                {
                                   'id': id
                                 })
    db.session.commit()
    return {"message": "Product Delete"}, 200

@app.post('/product/update_sql')
def update_sql():
    form = request.get_json()
    if not form:
        return {"error": "No input data provided"}, 400
    if not form.get('id'):
        return {"error": "ID is Required"}, 400
    if not form.get('name'):
        return {"error": "Name is Required"}, 400
    if not form.get('price'):
        return {"error": "Price is Required"}, 400
    if not form.get('stock'):
        return {"error": "Stock is Required"}, 400
    is_exiting = get_product_by_id_sql(form.get('id'))
    if is_exiting.get('error'):
        return {"error": "Product ID is not found"}, 400

    id = form.get('id')
    name = form.get('name')
    price = form.get('price')
    stock = form.get('stock')
    sql = text("""Update product 
                  set name = :name, price = :price, stock = :stock 
                  where id = :id""")
    result = db.session.execute(sql,
                                {
                                    'id': id,
                                    'name': name,
                                    'price': price,
                                    'stock': stock
                                 })
    db.session.commit()
    return {"message": "Update inserted", "product": get_product_by_id_sql(id)}, 200
