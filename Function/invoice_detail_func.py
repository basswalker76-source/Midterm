from app import db
from flask import request
from model.invoice import Invoice
from model.invoice_detail import InvoiceDetail
from model.product import Product
from sqlalchemy import text

def detail_listing():
    sql = text("SELECT * FROM invoice_detail")
    result = db.session.execute(sql)
    invoice_details = [
        {
            'id': row.id,
            'invoice_id': row.invoice_id,
            'product_id': row.product_id,
            'quantity': row.quantity,
            'price': float(row.price),
            'subtotal': float(row.subtotal)
        }
        for row in result
    ]
    return {"invoice_details": invoice_details}, 200

def get_detail_by_invoice_id(invoice_id: int):
    sql = text("""SELECT * FROM invoice_detail where invoice_id = :invoice_id""")
    result = db.session.execute(sql,{"invoice_id": invoice_id})
    invoice_details = [
        {
            'id': row.id,
            'invoice_id': row.invoice_id,
            'product_id': row.product_id,
            'quantity': row.quantity,
            'price': float(row.price),
            'subtotal': float(row.subtotal)
        }
        for row in result
    ]
    return {"invoice_details": invoice_details}, 200

def get_detail_by_id(id: int):
    sql = text("""SELECT * FROM invoice_detail WHERE id = :id""")
    result = db.session.execute(sql, {"id": id}).fetchone()

    if not result:
        return {"error": "Invoice not found"}

    return {
            'id': result.id,
            'invoice_id': result.invoice_id,
            'product_id': result.product_id,
            'quantity': result.quantity,
            'price': float(result.price),
            'subtotal': float(result.subtotal)
    }

def update_invoice_total(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return

    total = db.session.query(
        db.func.sum(InvoiceDetail.subtotal)
    ).filter(InvoiceDetail.invoice_id == invoice_id).scalar() or 0

    invoice.total_amount = total
    db.session.commit()

def detail_create():
    form = request.get_json(silent=True) or request.form
    product_id = form.get('product_id')
    quantity = form.get('quantity')
    invoice_id = form.get('invoice_id')

    if not product_id or not quantity or not invoice_id:
        return {"error": "product_id, quantity, and invoice_id are required"}, 400

    product = Product.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404

    price = product.price
    quantity = int(quantity)
    subtotal = price * quantity

    new_detail = InvoiceDetail(
        product_id=product_id,
        invoice_id=invoice_id,
        price=price,
        quantity=quantity,
        subtotal=subtotal
    )

    db.session.add(new_detail)
    db.session.commit()
    update_invoice_total(invoice_id)

    return {
        "message": "Invoice detail created successfully",
        "data": {
            "invoice_id": invoice_id,
            "product_id": product_id,
            "price": price,
            "quantity": quantity,
            "subtotal": subtotal
        }
    }, 201

def detail_delete():
    form = request.get_json(silent=True) or request.form
    detail_id = form.get("id")
    if not detail_id:
        return {"error": "Detail ID required"}, 400

    detail = InvoiceDetail.query.get(detail_id)
    if not detail:
        return {"error": "Detail not found"}, 404

    invoice_id = detail.invoice_id
    db.session.delete(detail)
    db.session.commit()
    update_invoice_total(invoice_id)

    return {"message": f"Invoice detail with id {detail_id} deleted"}, 200

def detail_update():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400

    detail_id = form.get("id")
    product_id = form.get("product_id")
    quantity = form.get("quantity")
    invoice_id = form.get("invoice_id")  # allow invoice_id update

    if not detail_id:
        return {"error": "No detail ID provided"}, 400

    detail = InvoiceDetail.query.get(detail_id)
    if not detail:
        return {"error": "Invoice detail not found"}, 404

    changes = False

    if invoice_id and int(invoice_id) != detail.invoice_id:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return {"error": "Invoice not found"}, 404
        detail.invoice_id = invoice.id
        changes = True

    if product_id and int(product_id) != detail.product_id:
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404
        detail.product_id = product.id
        detail.price = product.price  # update price from product
        changes = True

    if quantity and int(quantity) != detail.quantity:
        detail.quantity = int(quantity)
        changes = True

    if changes:
        detail.subtotal = detail.price * detail.quantity

    if not changes:
        return {"message": "No changes detected"}, 200

    db.session.commit()
    update_invoice_total(detail.invoice_id)

    return {
        "message": f"Invoice detail with id {detail_id} updated successfully",
        "detail": {
            "id": detail.id,
            "invoice_id": detail.invoice_id,
            "product_id": detail.product_id,
            "price": detail.price,
            "quantity": detail.quantity,
            "subtotal": detail.subtotal,
        },
    }, 200