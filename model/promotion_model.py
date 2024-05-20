from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
import datetime

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
 
class Promotions:
    def __init__(self, id=None, name=None, description=None, is_active=1, start_at=None, end_at=None, discount_value=None):
        self.id = id
        self.name = name
        self.description = description
        self.is_active = is_active
        self.start_at = start_at
        self.end_at = end_at
        self.discount_value = discount_value

    def to_dict(self):
        promotion_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'start_at': self.start_at,
            'end_at': self.end_at,
            'discount_value': self.discount_value
        }
        return promotion_dict
    
class PromotionModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_all_promotion(self):
        query = f"SELECT * FROM promotions"
        self.cur.execute(query)
        
        results = self.cur.fetchall()
        list_promotion = []
        for result in results:
            promotion = Promotions(id=result['id'],
                               name=result['name'],
                               description=result['description'],
                               is_active=result['is_active'],
                               start_at=result['start_at'],
                               end_at=result['end_at'],
                               discount_value=result['discount_value']
                               )
            list_promotion.append(promotion.to_dict())
        self.con.commit()
        print('list_promotion: ',list_promotion)
        return jsonify(list_promotion), 200
    
    def add_promotion(self, data):
        try:             
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
        
            query = f"INSERT INTO promotions (name, description, is_active, start_at, end_at, discount_value) \
                        VALUES ('{data['name']}', '{data['description']}', {data['is_active']} , '{data['start_at']}','{data['end_at']}', {data['discount_value']})"
            
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "insert promotion successfully"
            })
        except:
            print("error")
            return jsonify({
                "message" : "error"
            })
            
    def update_promotion(self, promotion_id, data):
        print("id: ", promotion_id)
        print("request.json: ", data)
        # Chuyển đổi định dạng ngày giờ
        start_at = datetime.datetime.strptime(data['start_at'], '%Y-%m-%dT%H:%M')
        end_at = datetime.datetime.strptime(data['end_at'], '%Y-%m-%dT%H:%M')
        try:
            query = f"UPDATE promotions SET \
                        name = '{data['name']}', \
                        description = '{data['description']}', \
                        is_active = {data['is_active']}, \
                        start_at = '{start_at.strftime('%Y-%m-%d %H:%M:%S')}', \
                        end_at = '{end_at.strftime('%Y-%m-%d %H:%M:%S')}', \
                        discount_value = {data['discount_value']} \
                        WHERE id = {promotion_id}"
            
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "update promotion successfully"
            })
        except Exception as e:
            print("error", e)
            return jsonify({
                "message": e
            })
                
    def delete_promotion(self, promotion_id):
        try:
            query = f"DELETE FROM promotions WHERE id = {promotion_id}"
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "delete promotion successfully"
            })
        except:
            print("error")
            return jsonify({
                "message": "error"
            })
            
    def get_all_promotion_is_valid(self):
        try:
            query = "SELECT * FROM promotions WHERE is_active = 1 \
                AND end_at > NOW()"
            self.cur.execute(query)
            
            results = self.cur.fetchall()
            list_promotion = []
            for result in results:
                promotion = Promotions(id=result['id'],
                                name=result['name'],
                                description=result['description'],
                                is_active=result['is_active'],
                                start_at=result['start_at'],
                                end_at=result['end_at'],
                                discount_value=result['discount_value']
                                )
                list_promotion.append(promotion.to_dict())
            print("list_promotion: ", list_promotion)
            self.con.commit()
            return jsonify(list_promotion)
            
        except Exception as e:
            print("error", e)
            return jsonify({
                "msg": str(e)
            })