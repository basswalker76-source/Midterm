from app import db
from sqlalchemy import text
import os
from PIL import Image, ImageDraw, ImageFont
from model.user import User
from model.invoice import Invoice
from flask import request
from datetime import datetime
from werkzeug.security import generate_password_hash

def user_listing():
    sql = text("SELECT * FROM user")
    result = db.session.execute(sql)
    users = [
        {
            'id': row.id,
            'user_name': row.user_name,
            'created_at': row.created_at,
            'email': row.email,
            'profile': row.profile,
            'password': row.password
        }
        for row in result
    ]
    return {"users": users}, 200

def get_user_by_id(id: int) -> dict:
    sql = text("SELECT id, user_name, created_at, email, profile FROM user WHERE id = :id")
    result = db.session.execute(sql, {"id": id}).fetchone()

    if result:
        return {
            'id': result.id,
            'user_name': result.user_name,
            'created_at': result.created_at,
            'email': result.email,
            'profile': result.profile,
        }

    return {"error": "User not found"}

def user_create():
    form = request.get_json(silent=True) or request.form

    if not form or not form.get('user_name') or not form.get('password'):
        return {"error": "Please fill all required fields"}, 400

    user_name = form.get('user_name').strip()
    email = form.get('email', '').strip() or None
    password = form.get('password').strip()

    profile_file = request.files.get('profile')
    file_name = None
    if profile_file:
        err = validate_image_type(profile_file) or validate_image_size(profile_file)
        if err:
            return err, 400
        file_name = profile_file.filename
        save_path = f'static/image/user/{file_name}'
        profile_file.save(save_path)
        watermark_image(save_path)

    existing_user = User.query.filter_by(user_name=user_name).first()
    if existing_user:
        return {"error": "Username already exists"}, 400

    if email:
        existing_email = User.query.filter(
            User.email.isnot(None), User.email == email
        ).first()
        if existing_email:
            return {"error": "Email already exists"}, 400

    hashed_pw = generate_password_hash(password)
    user = User(
        user_name=user_name,
        password=hashed_pw,
        email=email,
        profile=file_name,
        created_at=datetime.now()
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "User created successfully",
        "user": get_user_by_id(user.id)
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

def watermark_image(image_path, watermark_text="© Skyer"):
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

def user_delete():
    form = request.get_json(silent=True) or request.form
    if not form or not form.get("id"):
        return {"error": "No user id provided"}, 400

    user_id = form.get("id")
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    linked_invoice = Invoice.query.filter_by(user_id=user_id).first()
    if linked_invoice:
        return {
            "error": "Cannot delete this user because it is linked to existing invoices."
        }, 400

    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User with id {user_id} deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

def user_update():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "Please fill all required fields"}, 400

    user_id = form.get("id")
    user_name = form.get("user_name")

    if not user_id or not user_name:
        return {"error": "Please fill all required fields"}, 400

    user_id = int(user_id)
    user_name = user_name.strip()
    email = (form.get("email") or "").strip() or None

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    existing_user = User.query.filter(
        User.user_name == user_name,
        User.id != user_id
    ).first()
    if existing_user:
        return {"error": "Username already exists"}, 400

    new_profile = user.profile
    profile_file = request.files.get('profile')
    if profile_file:
        err = validate_image_type(profile_file) or validate_image_size(profile_file)
        if err:
            return err, 400
        file_name = profile_file.filename
        save_path = f'static/image/user/{file_name}'
        profile_file.save(save_path)
        watermark_image(save_path)
        new_profile = file_name

    if email:
        existing_email = User.query.filter(
            User.email == email,
            User.id != user_id,
            User.email.isnot(None)
        ).first()
        if existing_email:
            return {"error": "Email already exists"}, 400

    if (user.user_name == user_name and
        user.profile == new_profile and
        user.email == email):
        return {"message": "No changes detected"}, 200

    user.user_name = user_name
    user.profile = new_profile
    user.email = email
    db.session.commit()

    return {
        "message": f"User with id {user_id} updated successfully",
        "user": {
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "created_at": user.created_at,
            "profile": user.profile
        }
    }, 200



