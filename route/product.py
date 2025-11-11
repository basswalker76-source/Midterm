from app import app
from Function.product_func import product_listing, product_create, product_adjust_stock, product_delete, product_update
@app.get('/product')
@app.get('/product/list')
def get_products():
    return product_listing()

@app.post('/product/create')
def create_product():
    return product_create()

@app.post('/product/adjust_stock')
def adjust_product():
    return product_adjust_stock()

@app.post('/product/delete')
def delete_product():
    return product_delete()

@app.post('/product/update')
def update_product():
    return product_update()