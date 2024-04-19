from app import app
from model.user_model import UserModel
from flask import request, send_file
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.utils import secure_filename
import os
user_model = UserModel()

@app.route("/users/all", methods=["GET"])
@jwt_required()
def get_all_users():
    return user_model.get_all_user()

@app.route("/users/register", methods=["POST"])
def register_users():
    return user_model.register_user(request.form)


@app.route("/users/login", methods=["POST"])
def login_user():
    return user_model.login(request.form)

@app.route('/logout', methods=['POST'])
def logout_user():
    return user_model.logout()

@app.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_test():
    return user_model.refresh()

@app.route('/api/example', methods=['GET'])
@jwt_required()
def route_protected():
    return user_model.protected()

@app.route('/update/<int:id>', methods=['POST'])
@jwt_required()
def update_user(id): 
    if request.method == 'POST':
        file = request.files['url_image']
        filename = secure_filename(file.filename)
        print("filename: ", filename)

        # Ensure the UPLOAD_FOLDER directory exists
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Save the file
        file.save(os.path.join(upload_folder, filename))

    result = user_model.update(request.form, id, filename)
    return result