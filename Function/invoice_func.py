from app import db
from flask import request
from model.invoice import Invoice
from model.user import User
from model.invoice_detail import InvoiceDetail
from Function.invoice_detail_func import update_invoice_total
from datetime import datetime
from sqlalchemy import text

def invoice_listing():
    sql = text("SELECT * FROM invoice")
    result = db.session.execute(sql)
    invoices = [
        {
            'id': row.id,
            'user_id': row.user_id,
            'date': row.date,
            "total_amount": float(row.total_amount),
        }
        for row in result
    ]
    return {"invoices": invoices}, 200

def get_invoice_by_user_id(user_id: int):
    sql = text("""SELECT * FROM invoice where user_id = :user_id""")
    result = db.session.execute(sql,{"user_id": user_id})
    invoices = [
        {
            'id': row.id,
            'user_id': row.user_id,
            'date': row.date,
            "total_amount": float(row.total_amount),
        }
        for row in result
    ]
    return {"invoices": invoices}, 200

def get_invoice_by_id(id: int):
    sql = text("""SELECT id, user_id, date, total_amount FROM invoice WHERE id = :id""")
    result = db.session.execute(sql, {"id": id}).fetchone()

    if not result:
        return {"error": "Invoice not found"}

    return {
        "id": result.id,
        "user_id": result.user_id,
        "date": result.date,
        "total_amount": float(result.total_amount),
    }

def invoice_create():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400

    user_id = form.get("user_id")
    if not user_id:
        return {"error": "No user ID provided"}, 400

    try:
        user_id = int(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    invoice = Invoice(user_id=user.id, total_amount=0)  # initially 0
    db.session.add(invoice)
    db.session.commit()

    return {
        "message": f"Invoice created successfully",
        "invoice": get_invoice_by_id(invoice.id),
    }, 201

def invoice_update():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400

    invoice_id = form.get("id")
    user_id = form.get("user_id")

    if not invoice_id:
        return {"error": "No invoice ID provided"}, 400
    if not user_id:
        return {"error": "No user ID provided"}, 400

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404

    try:
        user_id = int(user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    changes = False
    if invoice.user_id != user_id:
        invoice.user_id = user_id
        changes = True

    if not changes:
        return {"message": "No changes detected"}, 200

    db.session.commit()

    update_invoice_total(invoice.id)

    return {
        "message": f"Invoice with id {invoice.id} updated successfully",
        "invoice": get_invoice_by_id(invoice.id),
    }, 200

def invoice_delete():
    form = request.get_json(silent=True) or request.form
    if not form or not form.get("id"):
        return {"error": "No Invoice id provided"}, 400

    invoice_id = form.get("id")
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404

    linked_detail = InvoiceDetail.query.filter_by(invoice_id=invoice_id).first()
    if linked_detail:
        return {
            "error": "Cannot delete this Invoice because it is linked to existing Sale Detail."
        }, 400

    try:
        db.session.delete(invoice)
        db.session.commit()
        return {"message": f"Invoice with id {invoice_id} deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
