from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
from datetime import timezone
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, storage
import requests

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
class ProductImageModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_data(self):
        try:       
            query = """
                SELECT 
                product_images.id as id,
                products.name as product,
                product_images.url
                FROM product_images
                JOIN products on product_images.product_id = products.id
            """
            self.cur.execute(query)
            results = self.cur.fetchall()
            
            list_product_image = []
            for result in results:
                item = {
                    "id": result['id'],
                    "product": result['product'],
                    "url": result['url']
                }
                list_product_image.append(item)
                
            self.con.commit()
            return jsonify(list_product_image)
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
            
    def add_data(self, data):
        try:
            product = data.get('product')
            files = request.files.get('urls')
            print("product: ", product)
            print("files: ", files)
            
            image_file = files 
            print("image_file: ", image_file)
            if not image_file:
                return jsonify({'message': 'Không có ảnh được tải lên'}), 400
            
            # file_name = os.path.join('images',  image_file.filename)
            file_name = os.path.join('images', image_file.filename)
            
            # Tải ảnh lên Firebase Storage
            blob = bucket.blob(file_name)
            
            blob.content_type = image_file.content_type
            
            # Tải tệp lên từ file
            blob.upload_from_file(image_file)
            
            # Làm URL công khai (tùy chọn)
            blob.make_public()
            public_url = blob.public_url
            print("public_url: ", public_url)
            
            query = f"""
                INSERT INTO product_images (product_id, url)
                VALUES ({data['product']}, '{public_url}')
            """
            self.cur.execute(query)
            self.con.commit()
                
            return jsonify({
                "msg" : "add successfully"
            })
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
            
    def delete_data(self, id):
        try:
            query = """
                DELETE FROM product_images 
                WHERE id = %s
            """ 
            
            self.cur.execute(query, (id,))
            self.con.commit()
            
            return jsonify({
                "msg": "deleted successfully"
            })
            
        except Exception as e:
            return jsonify({
                "msg": str(e)
            })