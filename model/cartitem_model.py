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
  
class CartIemModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def view_cart_items(self, user_id):
        query = f"SELECT product_id, quantity, unit_price, size  FROM cart_items WHERE user_id = {user_id}"
        self.cur.execute(query)
        results = self.cur.fetchall()
        return jsonify(results) , 200
    
    def add_product_into_cart_items(self, user_id, data):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
        query = f"SELECT * FROM cart_items WHERE product_id = {data['productId']} and size = '{data['size']}'"
        self.cur.execute(query)
        results = self.cur.fetchall()
        
        if len(results) == 0:
            query_price_product = f"SELECT \
                                        products.id, \
                                        products.name, \
                                        products.price AS price, \
                                        CASE \
                                            WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN products.price \
                                            ELSE (products.price - promotions.discount_value) \
                                        END AS price_promote \
                                    FROM \
                                        products \
                                    LEFT JOIN \
                                        promotions \
                                    ON \
                                        products.promotion_id = promotions.id \
                                    WHERE products.id = {data['productId']}"
            
            self.cur.execute(query_price_product)
            product = self.cur.fetchone()
            print("price product: ", product['price_promote'])
            price_promote = product['price_promote']
            print("product : ", product)
            query_insert_product_into_cartitem = f"INSERT INTO cart_items(product_id, quantity, unit_price, user_id, create_at, size) VALUES ({data['productId']}, {data['quantity']}, {price_promote}, {user_id}, '{formatted_datetime}', '{data['size']}')"
            self.cur.execute(query_insert_product_into_cartitem)
            self.con.commit()
            return jsonify({
                "message": "successfully add product into cartitems"
            })

        querty_update_quantity_cartitem = f"UPDATE cart_items SET quantity = quantity + {data['quantity']} WHERE product_id = {data['productId']} and size = '{data['size']}'"
        self.cur.execute(querty_update_quantity_cartitem)
        self.con.commit()
        
        print("len result: ", len(results))
        return jsonify({
            "message": "successfully update quantity product into cartitems"
        })
        
    def delete_product_in_cart_items(self, user_id, list_id_cart_items):
        print("list id cart item : ", list_id_cart_items)
        if len(list_id_cart_items) != 0:
            for id in list_id_cart_items:
                query_delete_product_cart_items = f"DELETE FROM cart_items WHERE id = {id} and user_id = {user_id}"
                self.cur.execute(query_delete_product_cart_items)
                self.con.commit()
                
            return jsonify({
                "message" : "successfully"
            })
        return jsonify({
                "message" : "error"
            })          
    
    def update_product_in_cart_items(self, data, cart_items_id, user_id):
        query_update = f"UPDATE cart_items SET quantity = {data['quantity']}, size = '{data['size']}' WHERE id = {cart_items_id} and product_id = {data['product_id']} and user_id = {user_id}"
        self.cur.execute(query_update)
        self.con.commit()
        
        query_product_by_cart_items_id = f"SELECT product_id, quantity, unit_price, size FROM cart_items WHERE id = {cart_items_id} and user_id = {user_id}"
        self.cur.execute(query_product_by_cart_items_id)
        result = self.cur.fetchone()
        
        return jsonify({
            "message" : "successfully",
            "productId": result['product_id'],
            "quantity": result['quantity'],
            "unitPrice": result['unit_price'],
            "size": result['size']
        })

