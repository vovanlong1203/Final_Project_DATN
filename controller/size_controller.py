from app import app
from model.size_model import SizeModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
size_model = SizeModel()

@app.route("/api/size", methods=["GET"])
@jwt_required()
def get_all_size():
    return size_model.get_all()

@app.route("/api/size", methods=["POST"])
@jwt_required()
def add_size():
    return size_model.add_size(request.json)

@app.route("/api/size/<int:id>", methods=["PUT"])
@jwt_required()
def update_size(id):
    return size_model.update_size(id, request.json)

@app.route("/api/size/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_size(id):
    return size_model.delete_size(id)