import mysql.connector
from configs.config import dbconfig
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, storage
import mysql.connector
from mysql.connector import Error
import datetime

import os


cred = credentials.Certificate("demo1-55087-firebase-adminsdk-avom5-fc97a6fb42.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'demo1-55087.appspot.com'
        })
bucket = storage.bucket()

def connect_to_database():
    try:
        con = mysql.connector.connect(
                    host = dbconfig["host"],
                    user = dbconfig["username"],
                    password = dbconfig["password"],
                    database = dbconfig["database"])
        return con
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối đến cơ sở dữ liệu: {err}")
        return None

class User:
    def __init__(self, user_id=None,  full_name=None, gender=None, 
                 gmail=None, password=None, phone_number=None, role=None, 
                 url_image=None, username=None,birthday=None,address = None):        
        self.user_id = user_id
        self.full_name = full_name
        self.gender = gender
        self.gmail = gmail
        self.password = password
        self.phone_number = phone_number
        self.role = role
        self.url_image = url_image
        self.username = username
        self.birthday = birthday
        self.address = address
    def to_dict(self):
        return {
            'id': self.user_id,
            'full_name': self.full_name,
            'gender': self.gender,
            'gmail': self.gmail,
            'password': self.password,
            'phoneNumber': self.phone_number,
            'role': self.role,
            'urlImage': self.url_image,
            'username': self.username,
            'birthday': self.birthday,
            'address' : self.address

        }

class IndividualModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
 
    def get_user(self, user_id):
        try:
            query = f"SELECT * FROM users WHERE id = {user_id}"
            print('aaaaa')
            self.cur.execute(query)
            result = self.cur.fetchone()
        
            user = User(
                user_id=result['id'],
                full_name=result['full_name'],
                gender=result['gender'],
                gmail=result['gmail'],
                password=result['password'],
                phone_number=result['phone_number'],
                role=result['role'],
                url_image=result['url_image'],
                username=result['username'],
                birthday = result['birthday'],
                address = result['address']
            )
            return jsonify(
                user.to_dict()
            ), 200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': err
            })
    
    def upload_image(self, userId, avatar_file):
        try:
            # Tạo tên tệp duy nhất cho avatar
            file_name = os.path.join('avatars', f'{userId}_{avatar_file.filename}')
            
            # Tải avatar lên Firebase Storage
            blob = bucket.blob(file_name)
            blob.content_type = avatar_file.content_type
            blob.upload_from_file(avatar_file)
            blob.make_public()  # Làm URL công khai
            public_url = blob.public_url
            print(public_url)
            
            # Cập nhật URL của avatar trong cơ sở dữ liệu
            query_update_avatar = """
                UPDATE users 
                SET url_image = %s
                WHERE id = %s
            """
            self.cur.execute(query_update_avatar, (public_url, userId))
            self.con.commit()

            # Trả về thông báo thành công với mã trạng thái HTTP 201
            return jsonify({
                "message": "Cập nhật ảnh đại diện thành công."
            }), 201

        except Exception as e:
            print(f"Lỗi: {e}")
            # Nếu có lỗi xảy ra, ném nó lên lớp gọi để xử lý
            raise

    def update_user(self, data, id):
        try:
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            # Khởi tạo câu lệnh SQL cơ bản
            query = "UPDATE users SET "

            # Tạo danh sách các trường cần cập nhật
            fields_to_update = []

            # Kiểm tra và thêm các trường đã có dữ liệu trong data vào danh sách fields_to_update
            if 'full_name' in data:
                fields_to_update.append(f"full_name = '{data['full_name']}'")
            if 'gender' in data:
                fields_to_update.append(f"gender = '{data['gender']}'")
            if 'phoneNumber' in data:
                fields_to_update.append(f"phone_number = '{data['phoneNumber']}'")
            if 'birthday' in data:
                fields_to_update.append(f"birthday = '{data['birthday']}'")
            if 'email' in data:
                fields_to_update.append(f"gmail = '{data['email']}'")
            
            # Nếu có ít nhất một trường được cập nhật, thực hiện câu lệnh SQL UPDATE
            if fields_to_update:
                query += ", ".join(fields_to_update)
                query += f", update_at = '{formatted_datetime}' WHERE id = {id}"

                # Thực hiện câu lệnh SQL UPDATE
                self.cur.execute(query)
                self.con.commit()
                print("update thành công.")
                
                return self.get_user(id)
            else:
                # Nếu không có trường nào được cập nhật, trả về thông báo lỗi
                return jsonify({
                    "message": "Không có trường nào được cập nhật"
                }), 400
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                "message": "error"
            }), 500
