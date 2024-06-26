from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
import datetime
from datetime import timezone
from datetime import timedelta
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required,
    unset_access_cookies, 
    get_jwt
)
from werkzeug.utils import secure_filename
from configs.connection import connect_to_database

    
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
    # trường birthday, address, thêm role vào json trong login  
    def __init__(self, user_id=None, is_enabled=1, is_locked=0, create_at=None, 
                 update_at=None, account_provider=None, full_name=None, gender=None, 
                 gmail=None, password=None, phone_number=None, role=None, 
                 url_image=None, username=None, birthday=None):        
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
        self.birthday = birthday
        
    def to_dict(self):
        return {
            'id': self.user_id,
            'is_enabled': self.is_enabled,
            'is_locked': self.is_locked,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'account_provider': self.account_provider,
            'full_name': self.full_name,
            'gender': self.gender,
            'gmail': self.gmail,
            'password': self.password,
            'phoneNumber': self.phone_number,
            'role': self.role,
            'urlImage': self.url_image,
            'username': self.username,
            'birthday': self.birthday
        }
    
            
class UserModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
         
    #input: full_name, gmail, username, password
    def register_user(self, data):
        try:
            query_find_username = f"SELECT * FROM users WHERE username = '{data['username']}'"
            self.cur.execute(query_find_username)
            if self.cur.fetchone():
                print("Tên người dùng đã tồn tại.")
                return jsonify({
                    "message" : "user is exist"
                }), 400
            query_find_gmail = f"SELECT * FROM users WHERE gmail = '{data['gmail']}'"
            self.cur.execute(query_find_gmail)
            if self.cur.fetchone():
                print("gmail đã tồn tại.")
                return jsonify({
                    "message" : "gmail is exist"
                }), 400
            
            current_datetime = datetime.datetime.now()
            print("data: ", data)
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_insert_user = f"INSERT INTO users (is_enabled, is_locked, create_at, update_at, account_provider, full_name, gmail, password, role, username) VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s, %s, %s)"
            user = User(
                is_enabled=1,
                is_locked=0,
                create_at=formatted_datetime,
                update_at=formatted_datetime,
                account_provider=AccountProvider.LOCAL.value,
                full_name=data.get('full_name'),
                gmail=data.get('gmail'),
                password=data.get('password'),
                role= Role.USER.value,
                username=data.get('username')
            )
            user_data = user.to_dict()
            user_values = (
                user_data['is_enabled'],
                user_data['is_locked'],
                user_data['account_provider'],
                user_data['full_name'],
                user_data['gmail'],
                user_data['password'],
                user_data['role'],
                user_data['username']
            )
            self.cur.execute(query_insert_user, user_values)
            self.con.commit()
            print("Người dùng đã được đăng ký thành công.")
            query_find_id_user = f"SELECT id FROM users WHERE username = '{user_data['username']}'"
            self.cur.execute(query_find_id_user)
            result = self.cur.fetchone()
            id = result['id']
            # Tạo access token và refresh token
            access_token = create_access_token(identity=id)
            refresh_token = create_refresh_token(identity=id)
            
            new_datetime = current_datetime + datetime.timedelta(days=30)
            formatted_datetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_insert_refresh = f"INSERT INTO token_refresh (reset_required, user_id, expiration_date, token) \
                                    VALUES ({0}, {id}, '{formatted_datetime}', '{refresh_token}')"
            self.cur.execute(query_insert_refresh)
            self.con.commit()
            
            return jsonify({
                "user_id": id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "message" : "user registered successfully"
            }), 201
            
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': str(err)
            }) , 500
                
    # input: Authorization: Bearer token
    def get_all_user(self):
        try:
            query = "SELECT * FROM users"
            self.cur.execute(query)
            self.con.commit()
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
            return jsonify(users), 200
            
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối đến cơ sở dữ liệu: {err}")
            return jsonify({
                "message": "error"
            }), 500
    
    # input: username, password
    def login(self, data):
        try:
            print("data login ", data)
            query_find_user = f"SELECT * FROM users WHERE username = '{data['username']}' and role = 'USER' and is_enabled = 1 and is_locked = 0"
            self.cur.execute(query_find_user)
            user = self.cur.fetchone()
            if not user:
                print("Tên người dùng không tồn tại.")
                return jsonify({
                    "message": "Tên người dùng không tồn tại."
                }), 401

            if user['password'] != data['password']:
                print("Mật khẩu không chính xác.")
                return jsonify({
                    "message": "Mật khẩu không chính xác."
                }), 401

            user_id = user['id']
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            
            current_datetime = datetime.datetime.now()
            new_datetime = current_datetime + datetime.timedelta(days=30)
            formatted_datetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_token = f"UPDATE token_refresh SET \
                            expiration_date = '{formatted_datetime}', \
                            token = '{refresh_token}' \
                            WHERE user_id = {user_id}"
            self.cur.execute(query_token)
            self.con.commit()
            
            query_role = f"SELECT role from users WHERE id = {user_id}"
            self.cur.execute(query_role)
            result = self.cur.fetchone()
            self.con.commit()
            
            response = jsonify({
                "message": "Đăng nhập thành công.",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id,
                "role" : result['role']
            })
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response , 200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': err
            }) , 500
    
    def login_admin(self, data):
        try:
            print("data ", data)
            query_find_user = f"SELECT * FROM users WHERE username = '{data['username']}' and role = 'ADMIN' and is_enabled = 1 and is_locked = 0"
            self.cur.execute(query_find_user)
            user = self.cur.fetchone()
            if not user:
                print("Tên người dùng không tồn tại.")
                return jsonify({
                    "message": "Tên người dùng không tồn tại."
                }), 401
                
            if user['password'] != data['password']:
                print("Mật khẩu không chính xác.")
                return jsonify({
                    "message": "Mật khẩu không chính xác."
                }), 401
                
            user_id = user['id']
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            
            current_datetime = datetime.datetime.now()
            new_datetime = current_datetime + datetime.timedelta(days=30)
            formatted_datetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_token = f"UPDATE token_refresh SET \
                            expiration_date = '{formatted_datetime}', \
                            token = '{refresh_token}' \
                            WHERE user_id = {user_id}"
            self.cur.execute(query_token)
            self.con.commit()
            
            query_role = f"SELECT role from users WHERE id = {user_id}"
            self.cur.execute(query_role)
            result = self.cur.fetchone()
            self.con.commit()
            
            response = jsonify({
                "message": "Đăng nhập thành công.",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id,
                "role" : result['role']
            })
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response , 200
        
            
        except Exception as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': str(err)
            }) , 500

    def logout(self):
        response = jsonify({
            'message': 'logout'
        })
        unset_jwt_cookies(response)
        unset_access_cookies(response)
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
    def get_count_user(self):
        try:
            query = "SELECT * FROM users"
            self.cur.execute(query)
            
            result = self.cur.fetchall()
            return jsonify(result) , 200
            
        except Exception as e:
            return jsonify({'msg': str(e)})

    def login_by_gg(self):
        try:
            gmail = request.args.get("gmail")
            fullname = request.args.get("fullName")
            urlImage = request.args.get("urlImage")
            
            print(gmail,fullname,urlImage)
            
            query_find_user = f"SELECT * FROM users WHERE gmail = '{gmail}'"
            self.cur.execute(query_find_user)
            user = self.cur.fetchone()
            if not user:
                print("Tên người dùng không tồn tại.")
                current_datetime = datetime.datetime.now()
                new_datetime = current_datetime + datetime.timedelta(days=30)
                formatted_datetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
                query_insert_gg = f"""
                    INSERT INTO users (is_enabled, is_locked, create_at, update_at, account_provider, full_name, url_image, gmail, username) 
                    VALUES (1, 0, '{current_datetime}','{current_datetime}', 'GOOGLE', '{fullname}', '{urlImage}', '{gmail}', '{gmail}')
                """
                self.cur.execute(query_insert_gg)
                self.con.commit()
                user_id = self.cur.lastrowid
            else:
                user_id = user['id']
                
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)
            
            current_datetime = datetime.datetime.now()
            new_datetime = current_datetime + datetime.timedelta(days=30)
            formatted_datetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_token = f"UPDATE token_refresh SET \
                            expiration_date = '{formatted_datetime}', \
                            token = '{refresh_token}' \
                            WHERE user_id = {user_id}"
            self.cur.execute(query_token)
            self.con.commit()
            
            query_role = f"SELECT role from users WHERE id = {user_id}"
            self.cur.execute(query_role)
            result = self.cur.fetchone()
            self.con.commit()
            
            response = jsonify({
                "message": "Đăng nhập thành công.",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id,
                "role" : result['role']
            })
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response , 200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': err
            })

    def get_count_users(self):
        try:
            query = "select count(*) as count from users"
            self.cur.execute(query)
            result = self.cur.fetchone()
            self.con.commit()
            count = result['count']
            return jsonify(
                int(count)
            )
        except Exception as e:
            print("error: ", str(e))    
            
    def get_user_admin(self):
        try:
            keyword = request.args.get('keyword', '').lower()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            offset = (page - 1) * limit
            
            if keyword:
                search_query = """
                    SELECT * FROM users
                    WHERE LOWER(full_name) LIKE %s
                    OR LOWER(username) LIKE %s
                    LIMIT %s OFFSET %s
                """
                search_keyword = f"%{keyword}%"
                self.cur.execute(search_query, (search_keyword, search_keyword, limit, offset))
            else:
                all_users_query = """
                    SELECT * FROM users
                    LIMIT %s OFFSET %s
                """
                self.cur.execute(all_users_query, (limit, offset))
            
            results = self.cur.fetchall()
            self.con.commit()
            users = []
            
            for result in results:
                user = {
                    'user_id': result['id'],
                    'is_enabled': result['is_enabled'],
                    'is_locked': result['is_locked'],
                    'create_at': result['create_at'],
                    'update_at': result['update_at'],
                    'account_provider': result['account_provider'],
                    'full_name': result['full_name'],
                    'gender': result['gender'],
                    'gmail': result['gmail'],
                    'password': result['password'],
                    'phone_number': result['phone_number'],
                    'role': result['role'],
                    'url_image': result['url_image'],
                    'username': result['username']
                }

                users.append(user)
            
            if keyword:
                count_query = """
                    SELECT COUNT(*) as count 
                    FROM users 
                    WHERE LOWER(full_name) LIKE %s
                """
                self.cur.execute(count_query, (search_keyword,))
            else:
                count_query = "SELECT COUNT(*) as count FROM users"
                self.cur.execute(count_query)
            
            total_items = self.cur.fetchone()['count']
            total_pages = (total_items + limit - 1) // limit
            self.con.commit()
            response = {
                'items': users,
                'totalPages': total_pages
            }
            return jsonify(response), 200
        
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "error", "error": str(e)}), 500
        
    def is_lock_user(self, id):
        try:
            query = """
                UPDATE users 
                SET is_locked = 1
                WHERE id = %s
            """
            self.cur.execute(query, (id,))
            self.con.commit()
            
            return jsonify({"message": "lock user successfully"}), 200
        except Exception as e:
            print("error: ", str(e))