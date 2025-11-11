from app import app
from Function.category_func import category_listing, category_create, category_update, category_delete

@app.get('/category')
@app.get('/category/list')
def get_category():
    return category_listing()

@app.post("/category/create")
def create_category():
    return category_create()

@app.post('/category/delete')
def delete_category():
    return category_delete()

@app.post('/category/update')
def update_category():
    return category_update()