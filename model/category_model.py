from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from configs.connection import connect_to_database

class Category:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description
        
    def to_dict(self):
        category_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        return category_dict
    
class CategoryModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_all(self):
        try: 
            query = f"SELECT * FROM categories"
            self.cur.execute(query)
            
            results = self.cur.fetchall()
            
            list_category = []
            for result in results:
                category = Category(id=result['id'],
                                    name=result['name'],
                                    description=result['description'])
                list_category.append(category.to_dict())
            self.con.commit()
            return jsonify(list_category)
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
    
    def add_category(self, data):
        try:
            query = f"INSERT INTO categories (name, description) \
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
            
    def update_category(self, category_id, data):
        try:
            query = f"UPDATE categories SET name = '{data['name']}', description = '{data['description']}' WHERE id = {category_id}"
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "Category updated successfully"
            })
        except Exception as e:
            print("Error: ", e)
            return jsonify({
                "msg": str(e)
            })
    
    def delete_category(self, category_id):
        try:
            query = f"DELETE FROM categories WHERE id = {category_id}"
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "Category deleted successfully"
            })
        except Exception as e:
            print("Error: ", e)
            return jsonify({
                "msg": str(e)
            })


    def get_count_category(self):
        try:
            query = "select count(*) as count from categories"
            self.cur.execute(query)
            result = self.cur.fetchone()
            self.con.commit()
            count = result['count']
            return jsonify(
                int(count)
            )
        except Exception as e:
            print("error: ", str(e))    