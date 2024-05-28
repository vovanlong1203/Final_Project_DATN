from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
import re
from configs.connection import connect_to_database
    
def is_valid_vietnamese_name(name):
    if not isinstance(name, str):
        name = str(name)
    pattern = re.compile(r"^[A-Za-z\sÀ-Ỹà-ỹ]+$")
    return bool(pattern.match(name))

def is_valid_phone_number(phone_number):
    if not isinstance(phone_number, str):
        phone_number = str(phone_number)
    pattern = re.compile(r"^\+84\d{9,10}$|^0\d{9,10}$")
    return bool(pattern.match(phone_number))

class Address:
    def __init__(self,id=None,
                  user_id=None,
                phoneNumber=None, 
                name=None, 
                address=None, 
                street=None, 
                isDefault=None, 
                wardCode=None, 
                districtId=None):  
        self.id = id      
        self.user_id = user_id
        self.address = address
        self.street = street
        self.isDefault = isDefault
        self.wardCode = wardCode
        self.districtId = districtId
        self.name = name
        self.phoneNumber = phoneNumber
        
    def to_dict(self):
        return {
            'user_id':self.user_id,
            'id': self.id,
            'address': self.address,
            'street': self.street,
            'isDefault': self.isDefault,
            'wardCode': self.wardCode,
            'districtId': self.districtId,
            'name': self.name,
            'phoneNumber': self.phoneNumber,
        }
    def abc(self):
        return {
            'user_id': self.user_id
        }
class AddressModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
         
    def get_all_address_by_userId(self,userId):
        try:
            query = f"SELECT * FROM address WHERE user_id ='{userId}' "
            self.cur.execute(query)
            results = self.cur.fetchall()
            self.con.commit()
            address = []
            
            for result in results:
                user = Address(
    
                    id=result['id'],
                    address=result['address'],
                    street=result['street'],
                    isDefault = False if result['isDefault'] == 0 else True,
                    wardCode=result['wardCode'],
                    districtId=result['districtId'],
                    name=result['full_name'],
                    phoneNumber=result['phone_number']
                )
                address.append(user.to_dict())
            return jsonify(address), 200
            
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối đến cơ sở dữ liệu: {err}")
            return jsonify({
                "message": "error"
            })
        

    def insert_user_address(self,userId,data):
        print(data)

        try:
            full_name = data.get("name")
            phone_number = data.get("phoneNumber")

            if not is_valid_vietnamese_name(full_name):
                return jsonify({
                    "message" : "Tên không hợp lệ"
                }),400
    
            if not is_valid_phone_number(phone_number):
                return jsonify({
                    "message" : "Số điện thoại không hợp lệ"
                }),400

            query_insert_address = f"INSERT INTO address (user_id, address, street, isDefault, wardCode, full_name, districtId, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            address = Address(
            
                user_id = userId,
                street = data.get('street'),
                name=data.get('name'),
                address=data.get('address'),
                isDefault=data.get('isDefault'),
                phoneNumber=data.get('phoneNumber'),
                wardCode= data.get('wardCode'),
                districtId=data.get('districtId')
        
            )
            address_data = address.to_dict()
            address_values = (
                address_data['user_id'],
                address_data['address'],
                address_data['street'],
                address_data['isDefault'],
                address_data['wardCode'],
                address_data['name'],
                address_data['districtId'],
                address_data['phoneNumber']
            )
            self.cur.execute(query_insert_address, address_values)
            self.con.commit()
            return jsonify({
                "message" : "Thêm địa chỉ thành công."
            }), 201
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': err
            })

    
    def update_user_address(self, userId,id, data):
        try:
            full_name = data.get("name")
            phone_number = data.get("phoneNumber")

            if not is_valid_vietnamese_name(full_name):
                return jsonify({
                    "message": "Tên không hợp lệ"
                }),400

            if not is_valid_phone_number(phone_number):
                return jsonify({
                    "message": "Số điện thoại không hợp lệ"
                }),400

            query_update_address = """
                UPDATE address 
                SET address = %s, street = %s, isDefault = %s, wardCode = %s, full_name = %s, districtId = %s, phone_number = %s
                WHERE id = %s
            """
            address_values = (
                data.get("address"),
                data.get('street'),
                data.get('isDefault'),
                data.get('wardCode'),
                data.get('name'),
                data.get('districtId'),
                data.get('phoneNumber'),
                id
            )

            self.cur.execute(query_update_address, address_values)
            self.con.commit()

            return jsonify({
                "message": "Cập nhật địa chỉ thành công."
            }), 200

        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': str(err)
            })

    def delete_address(self, userId, id):
        try:
            query_delete_address = """
                DELETE FROM address
                WHERE id = %s
            """
            self.cur.execute(query_delete_address, (id,))
            self.con.commit()

            if self.cur.rowcount == 0:
                return jsonify({
                    "message": "Không tìm thấy địa chỉ để xóa."
                }), 404
            else:
                return jsonify({
                    "message": "Xóa địa chỉ thành công."
                }), 200

        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': str(err)
            }), 500
        

            