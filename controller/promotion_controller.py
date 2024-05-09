from app import app
from model.promotion_model import PromotionModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)

promotion_model = PromotionModel()

@app.route("/api/promotion", methods=["GET"])
@jwt_required()
def get_all_promotion():
    return promotion_model.get_all_promotion()

@app.route("/api/promotion/valid", methods=["GET"])
@jwt_required()
def get_all_promotion_is_valid():
    return promotion_model.get_all_promotion_is_valid()

@app.route("/api/promotion", methods=["POST"])
@jwt_required()
def add_promotion():
    return promotion_model.add_promotion(request.json)

@app.route("/api/promotion/<int:id>", methods=["PUT"])
@jwt_required()
def update_promotion(id):
    return promotion_model.update_promotion(id, request.json)

@app.route("/api/promotion/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_promotion(id):
    return promotion_model.delete_promotion(id)

