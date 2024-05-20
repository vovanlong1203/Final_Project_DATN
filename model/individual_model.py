import mysql.connector
import random
import smtplib
from configs.config import dbconfig
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, storage
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage

import os

import configs.firebase_config
bucket = configs.firebase_config.get_bucket()

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
            self.con.commit()
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


    def send_OTP(self, gmail):
            otp = ''
            for i in range(6):
                otp += str(random.randint(0, 9))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            from_mail = 'thanhhoang15032002@gmail.com'
            server.login(from_mail, 'rbjs mfrr omqu xkmh')
            msg = EmailMessage()
            msg['Subject'] = "OTP Verification"
            msg['From'] = from_mail
            msg['To'] = gmail
            msg.set_content("Your OTP is: " + otp)
            server.send_message(msg)
            server.quit()  # Đóng kết nối SMTP sau khi gửi thành công
            return otp  # Trả về phản hồi khi gửi thành công
        


    def for_got_password(self, username):
        try:
            query_find_user = f"SELECT * FROM users WHERE username = '{username}' and role = 'USER' and is_enabled = 1 and is_locked = 0"
            self.cur.execute(query_find_user)
            user = self.cur.fetchone()

            # Lấy thời điểm hiện tại
            
            if not user:
                print("Tên người dùng không tồn tại.")
                return jsonify({
                    "message": "Tên người dùng không tồn tại."
                }), 401
            else:
                try:
                    otp = self.send_OTP(user['gmail'])
                    try:
                        query_delete=f"DELETE FROM otpset_password WHERE user_id = '{user['id']}'"
                        self.cur.execute(query_delete)
                        self.con.commit()


                        current_datetime = datetime.now()
                        expiration_time = current_datetime + timedelta(minutes=5)
                        formatted_datetime = expiration_time.strftime('%Y-%m-%d %H:%M:%S.%f')




                        query_add_otp = f"INSERT INTO otpset_password (user_id, expiration_time, otp_value) VALUES (%s, %s, %s)"
                        self.cur.execute(query_add_otp,(user['id'],formatted_datetime,otp))
                        self.con.commit()
                        return user['gmail'],200
                    except mysql.connector.Error as err:
                        print(f"Lỗi: {err}")
                        return jsonify({
                            'msg': err
                        }), 500

        
                except Exception as e:
                    print(f"Lỗi: {e}")
                    return jsonify({'message': 'Có lỗi khi gửi mã OTP.'}), 500
                  # Trả về phản hồi từ hàm send_OTP
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({
                'msg': err
            }), 500  # Trả về phản hồi lỗi nếu có lỗi kết nối đến cơ sở dữ liệu

    def verify_otp(self):
        username = request.args.get("username")
        otp = request.args.get("otp")
        print(username,otp)
        try:
            
            # Xác định user_id dựa trên username
            query_find_user_id = f"SELECT id FROM users WHERE username = '{username}'"
            self.cur.execute(query_find_user_id)
            user_id = self.cur.fetchone()
            print(user_id['id'])

            if not user_id:
                return jsonify({"message": "Tên người dùng không tồn tại."}), 404

            # Truy vấn bảng otpset_password để lấy thông tin về OTP
            query_get_otp = f"SELECT expiration_time, otp_value FROM otpset_password WHERE user_id = %s"
            self.cur.execute(query_get_otp, (int(user_id['id']),))
            otp_info = self.cur.fetchone()

            if not otp_info:
                return jsonify({"message": "Không tìm thấy thông tin OTP cho người dùng này."}), 404

            expiration_time_str=otp_info['expiration_time']
            stored_otp = otp_info['otp_value']

            # Kiểm tra xem thời gian hiện tại có nằm trong khoảng thời gian hợp lệ không
            print(expiration_time_str)
            print(stored_otp)
            expiration_time = datetime.strptime(str(expiration_time_str), '%Y-%m-%d %H:%M:%S.%f')
            current_datetime = datetime.now()
            if current_datetime > expiration_time:
                return jsonify({"message": "OTP đã hết hạn."}), 400

            # Kiểm tra xem OTP được gửi lên có khớp với OTP lưu trữ không
            if otp != stored_otp:
                return jsonify({"message": "OTP không hợp lệ."}), 400

            # Nếu tất cả đều hợp lệ, trả về phản hồi thành công
            return jsonify({"message": "OTP hợp lệ."}), 200

        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            return jsonify({"message": "Có lỗi khi xác minh OTP."}), 500
