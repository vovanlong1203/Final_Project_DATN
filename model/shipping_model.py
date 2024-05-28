from flask import jsonify,request
import mysql.connector
import requests
from configs.config import dbconfig
from configs.connection import connect_to_database

class ShippingModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
            print("OKE")
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")



    def get_fee_ship(self):

        try:
            districtId = int(request.args.get("districtId"))
            wardCode = request.args.get("wardCode")
            if districtId is None or wardCode is None:
                return jsonify({"message": "Thiếu thông tin districtId hoặc wardCode"}), 400
            print(districtId, wardCode)
            # Dữ liệu payload
            payload_data = {
                "from_district_id": 1530,
                "from_ward_code": "40503",
                "service_id": 53320,
                "service_type_id": None,
                "to_district_id": districtId,
                "to_ward_code": str(wardCode),
                "height": 50,
                "length": 20,
                "weight": 200,
                "width": 20,
                "insurance_value": 10000,
                "cod_failed_amount": 2000,
                "coupon": None
            }

            # Header
            headers = {
                "token": "c61b8d62-a18d-11ee-a6e6-e60958111f48",
                "Content-Type": "application/json"
            }

            # Gửi yêu cầu POST đến API
            response = requests.post(
                "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee",
                json=payload_data,  # Truyền dữ liệu payload trong định dạng JSON
                headers=headers  # Truyền header
            )


            response_data = response.json()
            print(response_data.get("message",0))
            # Kiểm tra mã trạng thái của phản hồi
            if response.status_code == 200:
                response_data = response.json()
                total_value = response_data.get("data", {}).get("total", 0)
                return jsonify({"data": {"feeShip": total_value}}), 200
            else:
                print(f"Lỗi khi gọi API: {response.status_code}")
                return jsonify({"message": "Lỗi khi gọi API"}), response.status_code

        except Exception as e:
            print(f"Lỗi: {e}")
            return jsonify({"message": "Lỗi không xác định"}), 500