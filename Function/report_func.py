
from sqlalchemy import text, func
from app import db
from model.invoice_detail import InvoiceDetail
from model.invoice import Invoice
from model.user import User
from model.category import Category
from model.product import Product
from datetime import datetime, timedelta


def daily_sales_report(report_date):
    sql = text("""
        SELECT 
            i.date AS date,
            u.user_name AS customer,
            p.product_name,
            c.category_name,
            d.quantity,
            d.price,
            d.subtotal
        FROM invoice_detail d
        JOIN invoice i ON d.invoice_id = i.id
        JOIN product p ON d.product_id = p.id
        JOIN category c ON p.category_id = c.id
        JOIN "user" u ON i.user_id = u.id
        WHERE DATE(i.date) = :report_date
    """)
    rows = db.session.execute(sql, {"report_date": report_date}).fetchall()
    records = [dict(row._mapping) for row in rows]

    total_records = db.session.query(func.count(InvoiceDetail.id))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .filter(func.date(Invoice.date) == report_date).scalar() or 0

    total_products = db.session.query(func.sum(InvoiceDetail.quantity))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id) \
                         .filter(func.date(Invoice.date) == report_date).scalar() or 0

    total_income = db.session.query(func.sum(InvoiceDetail.subtotal))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .filter(func.date(Invoice.date) == report_date).scalar() or 0

    return {
        "report_date": report_date,
        "total_records": total_records,
        "total_products": total_products,
        "total_income": total_income,
        "records": records
    }

def weekly_sales_report(form):
    start_date = form.get("start_date")
    today_key = form.get("today")

    if start_date:
        try:
            base_date = datetime.fromisoformat(start_date).date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
        start = base_date
        end = base_date + timedelta(days=6)
        mode = "forward"
    elif today_key is not None:  # means user included 'today' key even it is empty
        base_date = datetime.now().date()
        start = base_date - timedelta(days=6)
        end = base_date
        mode = "reverse"
    else:
        return {"error": "Either 'start_date' or 'today' is required"}, 400

    sql = text("""
        SELECT 
            i.date AS date,
            u.user_name AS customer,
            p.product_name,
            c.category_name,
            d.quantity,
            d.price,
            d.subtotal
        FROM invoice_detail d
        JOIN invoice i ON d.invoice_id = i.id
        JOIN product p ON d.product_id = p.id
        JOIN category c ON p.category_id = c.id
        JOIN "user" u ON i.user_id = u.id
        WHERE DATE(i.date) BETWEEN :start_date AND :end_date
    """)

    rows = db.session.execute(sql, {"start_date": start, "end_date": end}).fetchall()
    records = [dict(row._mapping) for row in rows]

    total_records = db.session.query(func.count(InvoiceDetail.id)) \
    .join(Invoice, InvoiceDetail.invoice_id == Invoice.id) \
    .filter(func.date(Invoice.date).between(start, end)).scalar() or 0

    total_products = db.session.query(func.sum(InvoiceDetail.quantity)) \
    .join(Invoice, InvoiceDetail.invoice_id == Invoice.id) \
    .filter(func.date(Invoice.date).between(start, end)).scalar() or 0

    total_income = db.session.query(func.sum(InvoiceDetail.subtotal)) \
    .join(Invoice, InvoiceDetail.invoice_id == Invoice.id) \
    .filter(func.date(Invoice.date).between(start, end)).scalar() or 0

    return {
        "mode": mode,
        "records": records,
        "start_date": str(start),
        "end_date": str(end),
        "total_records": total_records,
        "total_products": total_products,
        "total_income": total_income
    }

def monthly_sales_report(year, month):
    year_month = f"{year}-{month:02d}"
    sql = text("""
        SELECT 
            i.date AS date,
            u.user_name AS customer,
            p.product_name,
            c.category_name,
            d.quantity,
            d.price,
            d.subtotal
        FROM invoice_detail d
        JOIN invoice i ON d.invoice_id = i.id
        JOIN product p ON d.product_id = p.id
        JOIN category c ON p.category_id = c.id
        JOIN "user" u ON i.user_id = u.id
        WHERE STRFTIME('%Y-%m', i.date) = :year_month
    """)
    rows = db.session.execute(sql, {"year_month": year_month}).fetchall()
    records = [dict(row._mapping) for row in rows]

    total_records = db.session.query(func.count(InvoiceDetail.id))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .filter(func.strftime('%Y-%m', Invoice.date) == year_month).scalar() or 0

    total_products = db.session.query(func.sum(InvoiceDetail.quantity))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .filter(func.strftime('%Y-%m', Invoice.date) == year_month).scalar() or 0

    total_income = db.session.query(func.sum(InvoiceDetail.subtotal))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .filter(func.strftime('%Y-%m', Invoice.date) == year_month).scalar() or 0

    return {
        "year_month": year_month,
        "total_records": total_records,
        "total_products": total_products,
        "total_income": total_income,
        "records": records
    }

def sales_by_criteria(product_id=None, category_id=None, user_id=None):
    # ------------------- RECORDS -------------------
    sql = text("""
        SELECT
            i.date AS date,
            u.user_name AS customer,
            p.product_name,
            c.category_name,
            d.quantity,
            d.price,
            d.subtotal
        FROM invoice_detail d
        JOIN invoice i ON d.invoice_id = i.id
        JOIN product p ON d.product_id = p.id
        JOIN category c ON p.category_id = c.id
        JOIN "user" u ON i.user_id = u.id
        WHERE 1=1
    """)

    params = {}
    if product_id:
        sql = text(str(sql) + " AND p.id = :product_id")
        params["product_id"] = product_id
    if category_id:
        sql = text(str(sql) + " AND c.id = :category_id")
        params["category_id"] = category_id
    if user_id:
        sql = text(str(sql) + " AND u.id = :user_id")
        params["user_id"] = user_id

    rows = db.session.execute(sql, params).fetchall()
    records = [dict(row._mapping) for row in rows]

    # ------------------- TOTALS -------------------
    query = db.session.query(func.count(InvoiceDetail.id).label("total_records"),
                             func.sum(InvoiceDetail.quantity).label("total_products"),
                             func.sum(InvoiceDetail.subtotal).label("total_income"))\
        .join(Invoice, InvoiceDetail.invoice_id == Invoice.id)\
        .join(Product, InvoiceDetail.product_id == Product.id)\
        .join(Category, Product.category_id == Category.id)\
        .join(User, Invoice.user_id == User.id)

    if product_id:
        query = query.filter(Product.id == product_id)
    if category_id:
        query = query.filter(Category.id == category_id)
    if user_id:
        query = query.filter(User.id == user_id)

    totals = query.first()

    return {
        "criteria": {
            "product_id": product_id,
            "category_id": category_id,
            "user_id": user_id
        },
        "total_records": totals.total_records or 0,
        "total_products": totals.total_products or 0,
        "total_income": totals.total_income or 0,
        "records": records
    }