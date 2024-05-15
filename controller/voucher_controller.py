from app import app
from model.voucher_model import VoucherModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)

voucher_model = VoucherModel()

@app.route("/api/admin/voucher", methods=["GET"])
@jwt_required()
def get_all_voucher():
    return voucher_model.get_all()

@app.route("/api/admin/voucher", methods=["POST"])
@jwt_required()
def add_voucher():
    return voucher_model.add_voucher(request.json)


@app.route("/api/admin/voucher/<int:id>", methods=["PUT"])
@jwt_required()
def update_voucher(id):
    return voucher_model.update_voucher(id, request.json)

@app.route("/api/admin/voucher/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_voucher(id):
    return voucher_model.delete_voucher(id)

