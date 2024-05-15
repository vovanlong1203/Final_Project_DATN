from app import app
from model.shipping_model import ShippingModel
from flask_jwt_extended import jwt_required
from flask_jwt_extended import (
    jwt_required
)
shipping_model=ShippingModel()
@app.route("/api/orders/fee-ship", methods=['GET'])
@jwt_required()
def getFeeShip(): 
    result = shipping_model.get_fee_ship()
    return result