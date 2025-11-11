from flask import jsonify, render_template
from app import app

@app.route("/")
def home():
    return render_template("hello_world.html")