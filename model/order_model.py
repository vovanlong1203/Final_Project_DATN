from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum


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
    
class Gender(Enum):
    CONFIRMED = 'Đã xác nhận'
    PACKAGING = 'Đóng gói'
    IN_TRANSIT = 'Đang giao'
    DELIVERED = 'Giao thành công'
    CANCELLED = 'Đã hủy'
    RETURN_EXCHANGE = 'Trả hàng/Đổi hàng'
    REFUNDED = 'Trả tiền'
    PREPARING_PAYMENT = 'Chuẩn bị thanh toán trực tuyến'
    
class OrderModel: 
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
        
    def get_discount_amount_product(self, id):
        try:
            print("dasdsad: ", id)
            total_discount_amount = 0
            query = f"""
                SELECT products.id as id, products.name as product, promotions.discount_value as discount_value
                FROM products 
                JOIN promotions
                ON products.promotion_id = promotions.id
                WHERE products.id = {id}
            """
            self.cur.execute(query)
            result = self.cur.fetchone()
            total_discount_amount += result['discount_value']

            return total_discount_amount
        except Exception as e:
            print("msg: ", str(e))
            return jsonify(str(e))
            
    def get_price_product(self, id):
        query = f"""
            SELECT products.id as id, products.name, products.price as price
            FROM products 
            WHERE products.id = {id}
        """
        self.cur.execute(query)
        result = self.cur.fetchone()
        price = result['price']
        
        return price
    
    def get_id_size(self, name):
        query = f"""
            SELECT id 
            FROM sizes 
            WHERE name = '{name}'
        """
        self.cur.execute(query)
        result = self.cur.fetchone()
        id = result['id']
        
        return id
    
    def order_product(self, data):
        try:
            cart_item = data['orderItems']
            print("data: ", data)
            total_amount = 0
            order_id = None
            for item in cart_item:
                discount_amount = self.get_discount_amount_product(item['productId'])
                price_product = self.get_price_product(item['productId'])
                total_amount += (price_product * item['quantity']) - (discount_amount *item['quantity'])
                print("discount_amount: ", discount_amount)
                print("total_amount: ", total_amount)
            
            totalAmount = total_amount + data['feeShip'] - data['discountAmount']
            
            
            print("data['discount_amount']: ", data['discountAmount'])
            print("data['discount_amount']: ", data['discountAmount'])
            print("", data['idsVoucher'])
            
            phoneNumber = data['phoneNumber']
            shippingAddress = data['shippingAddress']
            userId = data['userId']
            discountAmount = data['discountAmount']
            voucherId = str(data['idsVoucher'])
            paymentMethod = data['paymentMethod']
            if data['paymentMethod'] == "CASH":
                status = "CONFIRMED"
                query_order = f"""
                    INSERT INTO orders (total_amount, discount_amount, user_id, voucher_id, order_date, payment_method, phone_number, shipping_address, status)
                    VALUES ({totalAmount}, {discountAmount}, {userId}, '{voucherId}', NOW(), '{paymentMethod}', '{phoneNumber}', '{shippingAddress}', '{status}')
                """            
                self.cur.execute(query_order)
                self.con.commit()
                order_id = self.cur.lastrowid
                print("order_id: ", order_id)
            
            # if data['paymentMethod'] == "VNPAY":
            #     query_order = f"""
                
            #     """
                
            for item in cart_item:
                productId = item['productId']
                quantity = item['quantity']
                price_product = self.get_price_product(productId)
                query_order_item = """
                    INSERT INTO order_items(order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                """
                self.cur.execute(query_order_item, (order_id, productId, quantity, price_product))
                self.con.commit()
            
            for item in data['idsVoucher']:
                update_quantity_voucher = f"""
                    UPDATE vouchers 
                    SET usage_count = usage_count + 1
                    WHERE id = {item}
                """
                self.cur.execute(update_quantity_voucher)
                self.con.commit()
                
            for item in cart_item:
                id_cart_item = item['id']
                query_delete_cart_item = f"""
                    DELETE FROM cart_items 
                    WHERE id = {id_cart_item}
                """
                self.cur.execute(query_delete_cart_item)
                self.con.commit()
                
            for item in cart_item:
                id_product = item['productId']
                quantity = item['quantity']
                size = item['size']
                id_size = self.get_id_size(size)
                query_update_quantity_product =f"""
                    UPDATE product_size 
                    SET quantity = quantity - {quantity},
                        quantity_sold = quantity_sold + {quantity}
                    WHERE product_id = {id_product} AND
                        size_id = {id_size}
                """
                self.cur.execute(query_update_quantity_product)
                self.con.commit()
                
            return jsonify({
                "msg": "order successfully"
            })
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "error" : str(e) 
            })
    
                