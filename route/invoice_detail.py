from app import app, db
from Function.invoice_detail_func import (detail_listing, detail_create, detail_update, detail_delete, get_detail_by_invoice_id)
from flask import request
@app.get('/detail')
@app.get('/detail/list')
def detail_list():
    return detail_listing()
@app.get('/detail/list_by_invoice')
def list_by_invoice():
    data = request.get_json(silent=True) or request.form
    if not data:
        return {"error": "No input provided"}, 400

    invoice_id = data.get("invoice_id")
    if not invoice_id:
        return {"error": "invoice_id is required"}, 400

    return get_detail_by_invoice_id(int(invoice_id))

@app.post('/detail/create')
def create_detail():
    return detail_create()

@app.post('/detail/update')
def update_detail():
    return detail_update()

@app.post('/detail/delete')
def delete_detail():
    return detail_delete()