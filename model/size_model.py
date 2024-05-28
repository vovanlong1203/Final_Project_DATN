from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
from configs.connection import connect_to_database

    
class Gender(Enum):
    sizeS = 'S'
    sizeM = 'M'
    sizeL = 'L'
    sizeXL = 'XL'
    sizeXXL = 'XXL'

class Size:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description
        
    def to_dict(self):
        size_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        return size_dict
    
class SizeModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_all(self):
        try: 
            query = f"SELECT * FROM sizes"
            self.cur.execute(query)
            
            results = self.cur.fetchall()
            
            list_size = []
            for result in results:
                size = Size(id=result['id'],
                                    name=result['name'],
                                    description=result['description'])
                list_size.append(size.to_dict())
            self.con.commit()
            return jsonify(list_size)
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
    
    def add_size(self, data):
        try:
            query = f"INSERT INTO sizes (name, description) \
                VALUES ('{data['name']}', '{data['description']}')"
                
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "successfully"
            })
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
            
    def update_size(self, size_id, data):
        try:
            query = f"UPDATE sizes SET name = '{data['name']}', description = '{data['description']}' WHERE id = {size_id}"
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "size updated successfully"
            })
        except Exception as e:
            print("Error: ", e)
            return jsonify({
                "msg": str(e)
            })
    
    def delete_size(self, size_id):
        try:
            query = f"DELETE FROM sizes WHERE id = {size_id}"
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "size deleted successfully"
            })
        except Exception as e:
            print("Error: ", e)
            return jsonify({
                "msg": str(e)
            })

