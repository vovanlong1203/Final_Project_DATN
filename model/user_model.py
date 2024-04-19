from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
import datetime
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required
)
from werkzeug.utils import secure_filename

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
    
class AccountProvider(Enum):
    GOOGLE = 'google'
    LOCAL = 'local'

class Gender(Enum):
    FEMALE = 'female'
    MALE = 'male'

class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'
    
    
class User:
    def __init__(self, user_id=None, is_enabled=1, is_locked=0, create_at=None, 
                 update_at=None, account_provider=None, full_name=None, gender=None, 
                 gmail=None, password=None, phone_number=None, role=None, 
                 url_image=None, username=None):        
        self.user_id = user_id
        self.is_enabled = is_enabled
        self.is_locked = is_locked
        self.create_at = create_at
        self.update_at = update_at
        self.account_provider = account_provider
        self.full_name = full_name
        self.gender = gender
        self.gmail = gmail
        self.password = password
        self.phone_number = phone_number
        self.role = role
        self.url_image = url_image
        self.username = username
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'is_enabled': self.is_enabled,
            'is_locked': self.is_locked,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'account_provider': self.account_provider,
            'full_name': self.full_name,
            'gender': self.gender,
            'gmail': self.gmail,
            'password': self.password,
            'phone_number': self.phone_number,
            'role': self.role,
            'url_image': self.url_image,
            'username': self.username
        }
    
            
class UserModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def register_user(self, data):
        try:
            query_find_username = f"SELECT * FROM users WHERE username = '{data['username']}'"
            self.cur.execute(query_find_username)
            if self.cur.fetchone():
                print("Tên người dùng đã tồn tại.")
                return jsonify({
                    "message" : "user is exist"
                })
            query_find_gmail = f"SELECT * FROM users WHERE gmail = '{data['gmail']}'"
            self.cur.execute(query_find_gmail)
            if self.cur.fetchone():
                print("gmail đã tồn tại.")
                return jsonify({
                    "message" : "gmail is exist"
                })
            
            current_datetime = datetime.datetime.now()
            print("data: ", data)
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_insert_user = f"INSERT INTO users (is_enabled, is_locked, create_at, update_at, account_provider, full_name, gender, gmail, password, phone_number, role, url_image, username) VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            user = User(
                is_enabled=1,
                is_locked=0,
                create_at=formatted_datetime,
                update_at=formatted_datetime,
                account_provider=AccountProvider.LOCAL.value,
                full_name=data.get('full_name'),
                gender=data.get('gender'),
                gmail=data.get('gmail'),
                password=data.get('password'),
                phone_number=data.get('phone_number'),
                role= Role.USER.value,
                url_image=data.get('url_image'),
                username=data.get('username')
            )
            user_data = user.to_dict()
            user_values = (
                user_data['is_enabled'],
                user_data['is_locked'],
                user_data['account_provider'],
                user_data['full_name'],
                user_data['gender'],
                user_data['gmail'],
                user_data['password'],
                user_data['phone_number'],
                user_data['role'],
                user_data['url_image'],
                user_data['username']
            )
            self.cur.execute(query_insert_user, user_values)
            self.con.commit()
            print("Người dùng đã được đăng ký thành công.")
            # Tạo access token và refresh token
            access_token = create_access_token(identity=user_data["user_id"])
            refresh_token = create_refresh_token(identity=user_data["user_id"])
            return jsonify({
                "user_id": user.user_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "message" : "user registered successfully"
            })
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
                
    def get_all_user(self):
        try:
            query = "SELECT * FROM users"
            self.cur.execute(query)
            results = self.cur.fetchall()
            users = []
            
            for result in results:
                user = User(
                    user_id=result['id'],
                    is_enabled=result['is_enabled'],
                    is_locked=result['is_locked'],
                    create_at=result['create_at'],
                    update_at=result['update_at'],
                    account_provider=result['account_provider'],
                    full_name=result['full_name'],
                    gender=result['gender'],
                    gmail=result['gmail'],
                    password=result['password'],
                    phone_number=result['phone_number'],
                    role=result['role'],
                    url_image=result['url_image'],
                    username=result['username']
                )
                users.append(user.to_dict())
            return jsonify(users)
            
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối đến cơ sở dữ liệu: {err}")
            return jsonify({
                "message": "error"
            })
    
    def login(self, data):
        try:
            print("data login ", data)
            query_find_user = f"SELECT * FROM users WHERE username = '{data['username']}'"
            self.cur.execute(query_find_user)
            user = self.cur.fetchone()
            if not user:
                print("Tên người dùng không tồn tại.")
                return jsonify({
                    "message": "Tên người dùng không tồn tại."
                })

            if user['password'] != data['password']:
                print("Mật khẩu không chính xác.")
                return jsonify({
                    "message": "Mật khẩu không chính xác."
                })

            user_id = user['id']
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            
            response = jsonify({
                "message": "Đăng nhập thành công.",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id
            })
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response , 200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
    
    def logout():
        response = jsonify({
            'message': 'logout'
        })
        unset_jwt_cookies(response)
        return response, 200
        
    def refresh(self):
        # Create the new access token
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        # Set the JWT access cookie in the response
        resp = jsonify({'refresh': True})
        set_access_cookies(resp, access_token)
        return resp, 200
    
    def protected(self):
        try:
            username = get_jwt_identity()
            print(username)
            return jsonify({
                    "message": "oke",
                    "username": username
                })
        except: 
            return jsonify({
                "msg" : "error"
            })

    def update(self, data, id, url_image):
        try:
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query = f"UPDATE users SET full_name = '{data['full_name']}', gender = '{data['gender']}', phone_number = '{data['phone_number']}', url_image = '{url_image}', password = '{data['password']}', update_at = '{formatted_datetime}' WHERE id = {id}"

            self.cur.execute(query)
            self.con.commit()
            print("update thành công.")
            return jsonify({
                "message": "update successfully"
            }), 200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                "message" : "error"
            })
            
            