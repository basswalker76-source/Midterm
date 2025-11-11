from flask import jsonify

from app import app

@app.errorhandler(404)
def error_404(e):
    return jsonify({
        "status": 404,
        "message": "Page Not found"
    }), 404