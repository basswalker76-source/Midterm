from app import app
from flask import request
from Function.report_func import daily_sales_report, weekly_sales_report, monthly_sales_report, sales_by_criteria
from datetime import datetime

@app.get('/report/daily')
def daily_report():
    date = request.form.get("date")
    if not date:
        return {"error": "date is required"}, 400
    return daily_sales_report(date)

@app.get('/report/weekly')
def weekly_report():
    form = request.args or request.form
    report = weekly_sales_report(form)
    return report, 200

@app.get('/report/monthly')
def monthly_report():
    year = request.form.get("year")
    month = request.form.get("month")
    if not year or not month:
        return {"error": "year and month are required"}, 400
    return monthly_sales_report(int(year), int(month))

@app.get('/report/criteria')
def criteria_report():
    product_id = request.form.get("product_id")
    category_id = request.form.get("category_id")
    user_id = request.form.get("user_id")
    return sales_by_criteria(
        product_id=int(product_id) if product_id else None,
        category_id=int(category_id) if category_id else None,
        user_id=int(user_id) if user_id else None
    )
