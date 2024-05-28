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
import time
from configs.connection import connect_to_database
  
class CartIemModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def view_cart_items(self, user_id):
        query = f"SELECT id ,product_id as productId, quantity, unit_price as unitPrice, size  FROM cart_items WHERE user_id = {user_id}"
        self.cur.execute(query)
        results = self.cur.fetchall()
        print(results)
        self.con.commit()

        return jsonify(results) , 200
    
    def add_product_into_cart_items(self, user_id, data):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
        query = f"SELECT * FROM cart_items WHERE product_id = {data['productId']} and size = '{data['size']}' and user_id = {user_id}"
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

    # def update_product_in_cart_items(self, user_id, cart_items_id, data):
    #     try:
    #         query_update = """
    #         UPDATE cart_items 
    #         SET quantity = %s, size = %s 
    #         WHERE id = %s AND product_id = %s AND user_id = %s
    #         """
    #         self.cur.execute(query_update, (data['quantity'], data['size'], cart_items_id, data['productId'], user_id))
    #         self.con.commit()
            
    #         check_size = f"""SELECT * FROM cart_items 
    #                         WHERE size = '{data['size']}' and product_id = {data['productId']} and user_id = {user_id} """
    #         self.cur.execute(check_size)
    #         result_check_size = self.cur.fetchall()
            
    #         id_check_size = []
            
    #         for item in result_check_size:
    #             id_check_size.append(item['id'])
            
    #         print("id_check_size: ", id_check_size)
            
    #         if (len(id_check_size) > 1):
    #             query_update = f"""
    #                 UPDATE cart_items ci1
    #                 INNER JOIN (
    #                     SELECT size, SUM(quantity) AS quantity
    #                     FROM cart_items
    #                     WHERE product_id = {data['productId']} AND user_id = {user_id}
    #                     GROUP BY size
    #                 ) ci2 ON ci1.size = ci2.size
    #                 SET ci1.quantity = COALESCE(ci2.quantity, 0)
    #                 WHERE ci1.product_id = {data['productId']}
    #                 AND ci1.user_id = {user_id}
    #                 and ci1.size = '{data['size']}';
    #             """
    #             self.cur.execute(query_update)
    #             self.con.commit()
                
    #             delete_duplicate = f"""
    #                 DELETE ci1
    #                 FROM cart_items ci1
    #                 INNER JOIN (
    #                     SELECT MIN(id) AS id, size
    #                     FROM cart_items
    #                     WHERE product_id = {data['productId']} AND user_id = {user_id}
    #                     GROUP BY size
    #                     HAVING COUNT(*) > 1
    #                 ) ci2 ON ci1.size = ci2.size AND ci1.id <> ci2.id
    #                 WHERE ci1.product_id = {data['productId']}
    #                 AND ci1.user_id = {user_id};
    #             """
    #             self.cur.execute(delete_duplicate)
    #             self.con.commit()
                
    #             query_product_by_cart_items_id = f"""
    #                 SELECT product_id as productId, quantity, unit_price as unitPrice, size FROM cart_items 
    #                 WHERE id = {cart_items_id} and user_id = {user_id}
    #             """
    #             self.cur.execute(query_product_by_cart_items_id)
    #             result = self.cur.fetchone()
    #             self.con.commit()
                
    #             return jsonify({
    #                 "message" : "successfully",
    #                 "productId": result['productId'],
    #                 "quantity": result['quantity'],
    #                 "unitPrice": result['unitPrice'],
    #                 "size": result['size']
    #             }) 
            
            
    #         query_product_by_cart_items_id = f"""
    #             SELECT product_id as productId, quantity, unit_price as unitPrice, size FROM cart_items 
    #             WHERE id = {cart_items_id} and user_id = {user_id}"""
    #         self.cur.execute(query_product_by_cart_items_id)
    #         result = self.cur.fetchone()
            
    #         return jsonify({
    #             "message" : "successfully",
    #             "productId": result['productId'],
    #             "quantity": result['quantity'],
    #             "unitPrice": result['unitPrice'],
    #             "size": result['size']
    #         })
    #     except Exception as e:
    #         print("Exception", str(e))
    #         return jsonify({
    #             "message" : str(e)
    #         })

    def update_product_in_cart_items(self, user_id, cart_items_id, data):
        try:
            time.sleep(0.1)
            query_update = """
            UPDATE cart_items 
            SET quantity = %s, size = %s 
            WHERE id = %s AND product_id = %s AND user_id = %s
            """
            self.cur.execute(query_update, (data['quantity'], data['size'], cart_items_id, data['productId'], user_id))
            self.con.commit()
            time.sleep(0.2)
            query_check_size = """
            SELECT id, quantity FROM cart_items 
            WHERE size = %s AND product_id = %s AND user_id = %s
            """
            self.cur.execute(query_check_size, (data['size'], data['productId'], user_id))
            result_check_size = self.cur.fetchall()
            self.con.commit()
            print("result_check_size: ", result_check_size)
            if len(result_check_size) > 1:
                
                time.sleep(0.1)
                check_size = """
                    SELECT quantity FROM product_size 
                    WHERE product_id = %s AND size_id = (
                        SELECT id FROM sizes 
                        WHERE name = %s
                    )
                """
                self.cur.execute(check_size, (data['productId'], data['size']))
                result_size = self.cur.fetchone()
                self.con.commit()
                print(result_size)
                size = result_size['quantity']
                total_quantity = sum(item['quantity'] for item in result_check_size)
                
                if total_quantity > size:
                    total_quantity = size
                
                first_item_id = result_check_size[0]['id']
                second_item_id = result_check_size[1]['id']
                
                time.sleep(0.1)
                query_update_quantity = """
                UPDATE cart_items
                SET quantity = %s
                WHERE product_id = %s and size = %s and user_id = %s
                """
                self.cur.execute(query_update_quantity, (total_quantity, data['productId'], data['size'], user_id))
                self.con.commit()
                time.sleep(0.1)
                
                query_delete_duplicates = """
                DELETE FROM cart_items
                WHERE id != %s AND size = %s AND product_id = %s AND user_id = %s
                """
                cart_items_id = first_item_id if first_item_id < second_item_id else second_item_id
                
                self.cur.execute(query_delete_duplicates, (cart_items_id, data['size'], data['productId'], user_id))
                self.con.commit()
                # cart_items_id = first_item_id
            
            time.sleep(0.1)
            query_product_by_cart_items_id = """
            SELECT product_id as productId, quantity, unit_price as unitPrice, size 
            FROM cart_items 
            WHERE id = %s AND user_id = %s
            """
            self.cur.execute(query_product_by_cart_items_id, (cart_items_id, user_id))
            result = self.cur.fetchone()
            self.con.commit()
            if not result:
                raise Exception("Updated cart item not found")
            
            return jsonify({
                "message": "successfully",
                "productId": result['productId'],
                "quantity": result['quantity'],
                "unitPrice": result['unitPrice'],
                "size": result['size']
            })

        except Exception as e:
            print("Exception", str(e))
            return jsonify({
                "message": str(e)
            })


