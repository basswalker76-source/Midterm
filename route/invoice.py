from app import app
from Function.invoice_func import invoice_create, invoice_listing, invoice_update, invoice_delete, get_invoice_by_user_id
from flask import request
@app.get('/invoice')
@app.get("/invoice/list")
def invoice_list():
    return invoice_listing()
@app.get('/invoice/list_by_user')
def invoice_list_by_id():
    # Get JSON or form-data
    data = request.get_json(silent=True) or request.form
    if not data:
        return {"error": "No input provided"}, 400

    user_id = data.get("user_id")
    if not user_id:
        return {"error": "user_id is required"}, 400

    return get_invoice_by_user_id(int(user_id))
@app.post('/invoice/create')
def create_invoice():
    return invoice_create()
@app.post('/invoice/delete')
def delete_invoice():
    return invoice_delete()
@app.post('/invoice/update')
def update_invoice():
    return invoice_update()