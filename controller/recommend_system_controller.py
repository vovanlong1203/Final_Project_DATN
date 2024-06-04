from app import app
from model.recommend_system import Recommend_System
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
from configs.config_thread import lock
recommend_System = Recommend_System()

@app.route("/api/products/recommend-system/<int:userId>", methods=["GET"])
# @jwt_required()
def get_list_product_by_recommend(userId):
    with lock:
        print(userId)
        return recommend_System.get_list_product(userId)