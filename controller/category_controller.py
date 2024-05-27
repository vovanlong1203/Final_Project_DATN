from app import app
from model.category_model import CategoryModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
from configs.config_thread import lock

category_model = CategoryModel()

@app.route("/api/admin/category", methods=["GET"])
@jwt_required()
def get_all_category():
    with lock:
        return category_model.get_all()

@app.route("/api/admin/category", methods=["POST"])
@jwt_required()
def add_category():
    with lock:
        return category_model.add_category(request.json)

@app.route("/api/admin/category/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    with lock:
        return category_model.update_category(id, request.json)

@app.route("/api/admin/category/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    with lock:
        return category_model.delete_category(id)