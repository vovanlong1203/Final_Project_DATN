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
from configs.connection import connect_to_database
import configs.firebase_config
bucket = configs.firebase_config.get_bucket()

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
            
            
    def search_image_admin(self):
        try:
            
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            offset = (page - 1) * limit
            keyword = request.args.get('keyword', '').lower()  
            
            if keyword is not None:
                search_query = """
                    SELECT 
                        product_images.id as id,
                        products.name as product,
                        product_images.url
                        FROM product_images
                        JOIN products on product_images.product_id = products.id
                    WHERE LOWER(products.name) LIKE %s
                    LIMIT %s OFFSET %s
                """
                search_keyword = f"%{keyword}%"
                self.cur.execute(search_query, (search_keyword, limit, offset))
            else:
                # Câu truy vấn chính để lấy dữ liệu sản phẩm với phân trang
                query = """
                    SELECT 
                        product_images.id as id,
                        products.name as product,
                        product_images.url
                        FROM product_images
                        JOIN products on product_images.product_id = products.id
                    LIMIT %s OFFSET %s
                """
                self.cur.execute(query, (limit, offset))
            
            results = self.cur.fetchall()
            self.con.commit()
            list_product_image = []
            for result in results:
                item = {
                    "id": result['id'],
                    "product": result['product'],
                    "url": result['url']
                }
                list_product_image.append(item)
            
            if keyword is not None:
                count_query = """
                    SELECT COUNT(*) as total
                    FROM product_images 
                    LEFT JOIN products ON product_images.product_id = products.id
                    WHERE LOWER(products.name) LIKE %s
                """
                self.cur.execute(count_query, (search_keyword,))
            else:
                count_query = """
                    SELECT COUNT(*) as total
                    FROM product_size
                """
                self.cur.execute(count_query)
            
            total_items = self.cur.fetchone()['total']
            total_pages = (total_items + limit - 1) // limit 
            self.con.commit()

            response = {
                'items': list_product_image,
                'totalPages': total_pages,
            }
            
            return jsonify(response), 200
        except Exception as e:
            print("Error:", str(e))
            return jsonify({"msg": str(e)}), 500

        