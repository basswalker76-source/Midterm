from app import db
from sqlalchemy import text
import os
from PIL import Image, ImageDraw, ImageFont
from model.product import Product
from model.invoice_detail import InvoiceDetail
from flask import request

def product_listing():
    sql = text("SELECT * FROM product")
    result = db.session.execute(sql)
    products = [
        {
            'id': row.id,
            'product_name': row.product_name,
            'price': row.price,
            'stock': row.stock,
            'category_id': row.category_id,
            'image': row.image
        }
        for row in result
    ]
    return {"products": products}, 200

def get_product_by_id(id: int) -> dict:
    sql = text("SELECT id, product_name, price, stock, category_id,image FROM product WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()

    if result:
        return {
            'id': result.id,
            'product_name': result.product_name,
            'price': result.price,
            'stock': result.stock,
            'category_id': result.category_id,
            'image': result.image
        }

    return {"error": "Product not found"}

def product_create():
    form = request.get_json(silent=True) or request.form
    price = form.get('price')
    stock = form.get('stock')
    category_id = form.get('category_id')
    image_file = request.files.get('image')
    file_name = None
    if image_file:
        err = validate_image_type(image_file) or validate_image_size(image_file)
        if err:
            return err, 400
        file_name = image_file.filename
        save_path = f'static/image/product/{file_name}'
        image_file.save(save_path)
        watermark_image(save_path)

    if not form:
        return {"error": "No input provided"}, 400
    if not form.get('product_name'):
        return {"error": "No product name provided"}, 400
    if not form.get('price'):
        return {"error": "No price provided"}, 400
    if not form.get('category_id'):
        return {"error": "No Category ID provided"}, 400

    product_name = form.get('product_name')
    existing_product = Product.query.filter_by(product_name=product_name).first()
    if existing_product:
        return {"error": "Product already exists"}, 400

    product = Product(
        product_name=product_name,
        price=price,
        stock=stock,
        category_id=category_id,
        image=file_name
    )
    db.session.add(product)
    db.session.commit()

    return {
        "message": "Product Created",
        "product": get_product_by_id(product.id)
    }, 201

def validate_image_type(image_file):
    allowed = {'png', 'jpg', 'jpeg'}
    ext = os.path.splitext(image_file.filename)[1].lower().replace('.', '')
    if ext not in allowed:
        return {"error": "Only PNG, JPG, JPEG files are allowed"}
    return None

def validate_image_size(image_file, max_size_mb=2):
    image_file.seek(0, os.SEEK_END)
    size = image_file.tell()
    image_file.seek(0)
    if size > max_size_mb * 1024 * 1024:
        return {"error": f"File size exceeds {max_size_mb}MB"}
    return None

def watermark_image(image_path, watermark_text="© Skyer Products"):
    """
    Adds a visible watermark to the bottom-right corner of an image.
    Automatically scales font size based on image dimensions.
    """

    with Image.open(image_path).convert("RGBA") as img:
        watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)

        font_size = max(20, int(min(img.size) / 15))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = img.size[0] - text_width - 30
        y = img.size[1] - text_height - 30
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
        watermarked = Image.alpha_composite(img, watermark_layer).convert("RGB")
        watermarked.save(image_path, "JPEG")

def product_adjust_stock():
    form = request.form

    product_id = form.get('product_id')
    quantity = form.get('quantity')

    if not product_id:
        return {"error": "No Product ID provided"}, 400
    if quantity is None:
        return {"error": "No quantity provided"}, 400

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except ValueError:
        return {"error": "Product ID and quantity must be integers"}, 400

    product = Product.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404

    new_stock = (product.stock or 0) + quantity
    if new_stock < 0:
        return {
            "error": f"Removing overflow: only {product.stock} item(s) available in stock"
        }, 400

    product.stock = new_stock

    try:
        db.session.commit()
        action = "added to" if quantity > 0 else "removed from"
        return {
            "message": f"{abs(quantity)} item(s) {action} stock",
            "product": {
                "id": product.id,
                "product_name": product.product_name,
                "new_stock": product.stock
            }
        }, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def product_delete():
    form = request.get_json(silent=True) or request.form
    if not form or not form.get("id"):
        return {"error": "No Product id provided"}, 400

    product_id = form.get("id")
    product = Product.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404

    linked_detail = InvoiceDetail.query.filter_by(product_id=product_id).first()
    if linked_detail:
        return {
            "error": "Cannot delete this Product because it is linked to existing Sale Detail."
        }, 400

    try:
        db.session.delete(product)
        db.session.commit()
        return {"message": f"Product with id {product_id} deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def product_update():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400

    id = form.get("id")
    if not id:
        return {"error": "No product ID provided"}, 400

    product = Product.query.get(id)
    if not product:
        return {"error": "Product with this ID does not exist"}, 404

    product_name = form.get("product_name", product.product_name).strip()
    price = form.get("price", product.price)
    stock = form.get("stock", product.stock)
    category_id = form.get("category_id", product.category_id)

    if form.get("price") is not None:
        try:
            price = float(price)
        except ValueError:
            return {"error": "Price must be a number"}, 400

    if form.get("stock") is not None:
        try:
            stock = int(stock)
        except ValueError:
            return {"error": "Stock must be an integer"}, 400

    existing_product = Product.query.filter(
        Product.product_name == product_name,
        Product.id != int(id)
    ).first()
    if existing_product:
        return {"error": "Product name already exists"}, 400

    new_image = product.image

    image_file = request.files.get("image")
    if image_file:
        file_name = image_file.filename.strip()
        save_path = f'static/image/product/{file_name}'
        image_file.save(save_path)
        watermark_image(save_path)
        new_image = file_name

    if (
        product.product_name == product_name and
        product.price == price and
        product.stock == stock and
        product.category_id == category_id and
        product.image == new_image
    ):
        return {"message": "No changes detected"}, 200

    product.product_name = product_name
    product.price = price
    product.stock = stock
    product.category_id = category_id
    product.image = new_image

    db.session.commit()

    return {
        "message": f"Product with id {product.id} updated successfully",
        "product": get_product_by_id(product.id)
    }, 200

