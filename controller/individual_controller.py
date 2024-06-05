from app import app
from model.individual_model import IndividualModel
from flask import request, send_file
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import (
    jwt_required
)
import os
from configs.config_thread import lock
individual_model = IndividualModel()

@app.route("/api/users/<int:userId>", methods=['GET'])
@jwt_required()
def detail_user1(userId):
    with lock:
        print(userId)
        return individual_model.get_user(userId)

@app.route("/api/users/avatar/<int:userId>", methods=['PUT'])
@jwt_required()
def upload_avatar(userId):
    try:
        with lock:
            # Nhận tệp avatar từ yêu cầu
            avatar_file = request.files.get('avatar')
            if not avatar_file:
                print("co file")
                return jsonify({'message': 'Không có avatar được tải lên'}), 400
            # Trả về URL công khai của avatar
            return individual_model.upload_image(userId,avatar_file)
    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify({'message': 'Lỗi khi tải avatar lên'}), 500
    


@app.route("/api/users/<int:id>", methods=['PUT'])
@jwt_required()
def update_user(id): 
    print (request.json)
    result = individual_model.update_user(request.json, id )

    return result


@app.route("/api/auth/forgot-password", methods=['POST'])
def SenOTP(): 
    try:
        username = request.args.get("username")
        return  individual_model.for_got_password(username)

    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify({'message': 'Lỗi không nhận được username'}), 500


@app.route("/api/auth/verify-otp", methods=['POST'])
def VerifyOTP(): 
    return  individual_model.verify_otp()

@app.route("/api/auth/reset-password", methods = ['PUT'] )
def reset_password():
    return individual_model.reset_password(request.json)


@app.route("/api/users/<int:id>/change-password", methods=['POST'])
@jwt_required()
def change_password(id): 
    return individual_model.ChangePassword(id)