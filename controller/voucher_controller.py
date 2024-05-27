from app import app
from model.voucher_model import VoucherModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
from configs.config_thread import lock
voucher_model = VoucherModel()

@app.route("/api/admin/voucher", methods=["GET"])
@jwt_required()
def get_all_voucher():
    with lock:
        return voucher_model.get_all()

@app.route("/api/admin/voucher", methods=["POST"])
@jwt_required()
def add_voucher():
    with lock:
        return voucher_model.add_voucher(request.json)


@app.route("/api/admin/voucher/<int:id>", methods=["PUT"])
@jwt_required()
def update_voucher(id):
    with lock:
        return voucher_model.update_voucher(id, request.json)

@app.route("/api/admin/voucher/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_voucher(id):
    with lock:
        return voucher_model.delete_voucher(id)

@app.route("/api/vouchers", methods=["GET"])
@jwt_required()
def get_voucher():
    with lock:
        return voucher_model.get_voucher_by_type()
