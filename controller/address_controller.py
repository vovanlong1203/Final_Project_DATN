from app import app
from model.address_model import AddressModel
from flask import request
from flask_jwt_extended import (
 jwt_required
)
from configs.config_thread import lock

address_model = AddressModel()

@app.route("/api/users/<int:userId>/addresses", methods=["GET"])
@jwt_required()
def get_all(userId):
    with lock:
        return address_model.get_all_address_by_userId(userId)

@app.route("/api/users/<int:userId>/addresses", methods=["POST"])
@jwt_required()
def insert_address(userId):
    with lock:
        return address_model.insert_user_address(userId,request.json)

@app.route("/api/users/<int:userId>/addresses/<int:id>", methods=["PUT"])
@jwt_required()
def update_address(userId,id):
    with lock:
        return address_model.update_user_address(userId,id,request.json)

@app.route("/api/users/<int:userId>/addresses/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_address(userId,id):
    with lock:
        return address_model.delete_address(userId,id)
