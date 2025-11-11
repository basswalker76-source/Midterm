from model.user import User
from Function.user_func import validate_image_size, validate_image_type, watermark_image, get_user_by_id
from app import app, db, jwt
from sqlalchemy import text
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, get_jwt)
from datetime import datetime

@app.post('/register')
def register():
    form = request.get_json(silent=True) or request.form
    email = form.get('email') or None

    if not form:
        return {"error": "No input provided"}, 400

    user_name = form.get('user_name')
    password = form.get('password')
    if not user_name or not password:
        return {"error": "Username and password are required"}, 400

    existing_user = User.query.filter_by(user_name=user_name).first()
    if existing_user:
        return {"error": "User already exists"}, 400

    hashed_pw = generate_password_hash(password)

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

    user = User(
        user_name=user_name,
        password=hashed_pw,
        email=email,
        profile=file_name,
        created_at=datetime.now()
    )
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"user_name": user.user_name, "profile": user.profile}
    )
    return {
        "message": "User registered successfully",
        "user": get_user_by_id(user.id),
        "access_token": access_token
    }, 201

@app.post('/login')
def login():
    form = request.get_json(silent=True) or request.form
    if not form:
        return {"error": "No input provided"}, 400
    if not form.get('user_name'):
        return {"error": "Username is required"}, 400
    if not form.get('password'):
        return {"error": "Password is required"}, 400

    user_name = form.get('user_name')
    password = form.get('password')

    sql = text("""select * from user where user_name = :user_name """)
    result = db.session.execute(sql, {"user_name": user_name}).fetchone()
    if not result:
        return {"error": "Invalid username or password"}, 401

    user = dict(result._mapping)
    if not check_password_hash(user['password'], password):
        return {"error": "Invalid username or password"}, 401

    additional_claims = {
        "user_name": user['user_name'],
        "profile": user['profile']
    }
    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims=additional_claims
    )
    return{
        "message": "Login Successfully",
        "access_token": access_token
    }, 200
@app.get("/me")
@jwt_required()
def me():
    user = get_jwt_identity()
    return jsonify(
        user=user,
        info=get_jwt()
    )
@app.post('/protected')
@jwt_required()
def get_protected():

    return {
        "data": "Protected Data access granted",
    }, 200

REVOKED_JTIS = set()
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    return jwt_data["jti"] in REVOKED_JTIS

@app.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    REVOKED_JTIS.add(jti)
    return jsonify(msg="Access token revoked")

@app.post('/reset-password')
@jwt_required()
def reset_password():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "No input provided"}, 400

    old_password = data.get("old_password")
    new_password = data.get("new_password")
    user_id = get_jwt_identity()

    if not all([old_password, new_password]):
        return {"error": "Old and new password required"}, 400

    user = User.query.get(user_id)
    if not user.check_password(old_password):
        return {"error": "Old password is incorrect"}, 401

    user.set_password(new_password)
    db.session.commit()
    return {"message": "Password reset successfully"}, 200
