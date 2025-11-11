from app import app
from Function.user_func import user_listing, user_create, user_delete, user_update

@app.get('/user')
@app.get('/user/list')
def get_users():
    return user_listing()

@app.post("/user/create")
def create_user():
    return user_create()

@app.post('/user/delete')
def delete_user():
    return user_delete()

@app.post('/user/update')
def update_user():
    return user_update()