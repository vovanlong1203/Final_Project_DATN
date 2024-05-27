from app import app
from flask import jsonify, request, redirect
import mysql.connector
from configs.config import dbconfig
from enum import Enum
import hashlib
import requests
import string
import urllib.parse
import random
import datetime
import hmac
import time
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

def generate_random_string(length):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def hmac_sha512(key, data):
    return hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha512).hexdigest()

vnp_TmnCode = 'QXYFI1HX'  # Mã website của bạn trên VNPay
vnp_HashSecret = 'QJ48ZZ7RT26JA00W08KUQHFCGTWD649H'  # Chuỗi bí mật hash
vnp_Url = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # URL của VNPay (sử dụng sandbox để test)
vnp_ReturnUrl = f'http://{local_ip}:5000/vnpay_return'

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
            return 0
            
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
        time.sleep(0.1)
        return id
    
    def generate_unique_order_id(self):
        while True:
            order_id = generate_random_string(6)
            if self.is_unique_order_id(order_id):
                return order_id
    
    def is_unique_order_id(self,order_id):
        query = "SELECT COUNT(*) AS count FROM orders WHERE id = %s"
        self.cur.execute(query, (order_id,))
        result = self.cur.fetchone()
        return result['count'] == 0
    
    def order_product(self, data):
        try:
            cart_item = data['orderItems']
            urlPayment = None
            print("data: ", data)
            total_amount = 0
            for item in cart_item:
                discount_amount = self.get_discount_amount_product(item['productId'])
                price_product = self.get_price_product(item['productId'])
                total_amount += (price_product * item['quantity']) - (discount_amount *item['quantity'])
            
            totalProductAmount = total_amount
            totalAmount = total_amount + data['feeShip'] - data['discountAmount']
            
            phoneNumber = data['phoneNumber']
            shippingAddress = data['shippingAddress']
            userId = data['userId']
            discountAmount = data['discountAmount']
            voucherId = str(data['idsVoucher'])
            paymentMethod = data['paymentMethod']
            shippingFee = data['feeShip']
            discountShippingFee = data['discountShippingFee']
            orderId = self.generate_unique_order_id()            
            
            if data['paymentMethod'] == "CASH":
                status = "CONFIRMED"
                query_order = f"""
                    INSERT INTO orders (id, total_amount, discount_amount, user_id, voucher_id, order_date, payment_method, phone_number, shipping_address, status, totalProductAmount, shippingFee, discountShippingFee)
                    VALUES ('{orderId}', {totalAmount}, {discountAmount}, {userId}, '{voucherId}', NOW(), '{paymentMethod}', '{phoneNumber}', '{shippingAddress}', '{status}', {totalProductAmount}, {shippingFee}, {discountShippingFee})
                """            
                self.cur.execute(query_order)
                self.con.commit()
            
            elif data['paymentMethod'] == "VNPAY":
                urlPayment = self.create_payment(totalAmount, orderId)
                status = "UNCONFIRMED"
                query_order = f"""
                    INSERT INTO orders (id, total_amount, discount_amount, user_id, voucher_id, order_date, payment_method, phone_number, shipping_address, status, totalProductAmount, shippingFee, discountShippingFee, urlPayment)
                    VALUES ('{orderId}', {totalAmount}, {discountAmount}, {userId}, '{voucherId}', NOW(), '{paymentMethod}', '{phoneNumber}', '{shippingAddress}', '{status}', {totalProductAmount}, {shippingFee}, {discountShippingFee}, '{urlPayment}')
                """
                self.cur.execute(query_order)
                self.con.commit()
                
            for item in cart_item:
                productId = item['productId']
                quantity = item['quantity']
                size = item['size']
                price_product = self.get_price_product(productId)
                print("orderId: ", orderId)
                query_order_item = """
                    INSERT INTO order_items(order_id, product_id, quantity, unit_price, sizeType, rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cur.execute(query_order_item, (orderId, productId, quantity, price_product, size, 0))
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
                "urlPayment" : urlPayment,
                "orderId": orderId
            }), 200
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "error" : str(e) 
            }), 500
   
    def vnpay_return(self):
        vnp_ResponseCode = request.args.get('vnp_ResponseCode')
        print("vnp_ResponseCode", vnp_ResponseCode)
        vnp_TxnRef = request.args.get('vnp_TxnRef')  
        order_id = vnp_TxnRef
        if vnp_ResponseCode == '00':
            data = {
                "status" : "CONFIRMED"
            }
            self.update_status_order(order_id,data)
            return redirect('/vnpay_return?state=1')
        else:
            data = {
                "status" : "CANCELLED"
            }
            self.update_status_order(order_id,data)
            self.cancel_order(order_id)
            return redirect('/vnpay_return?state=0')   
    
    def get_all_order(self):
        try:
            query = f"""
                SELECT o.id, u.full_name, o.total_amount, o.payment_method, o.phone_number, o.shipping_address, o.status, o.order_date
                FROM orders o
                INNER JOIN users u
                ON o.user_id = u.id
            """          
            self.cur.execute(query)
            results = self.cur.fetchall()
            self.con.commit()
            
            list_order = []
            
            for result in results:
                list_order.append({
                    "id": result['id'],
                    "customer": result['full_name'],
                    "total_amount": result['total_amount'],
                    "payment_method": result['payment_method'],
                    "phone_number": result['phone_number'],
                    "shipping_address": result['shipping_address'],
                    "status": result['status'],
                    "order_date": result['order_date']
                })
            
            return jsonify(list_order)
        except Exception as e:
            print("error", str(e))
            return jsonify({
                "msg": str(e)
            }) , 500
            
    def update_status_order(self, id, data):
        try:
            query = f"""
                UPDATE orders
                SET status = %s
                WHERE id = %s
            """
            self.cur.execute(query, (data['status'], id))
            self.con.commit()
        except Exception as e:
            print("error", str(e))

            
    def get_list_order_item(self, orderId):
        try:
            query = f"""
                SELECT * FROM order_items 
                WHERE order_id = '{orderId}'
            """        
            
            self.cur.execute(query)
            results = self.cur.fetchall()
            self.con.commit()
            
            orderItemList = []
            
            for item in results:
                orderItemList.append({
                    "id" : item['id'],
                    "quantity": item['quantity'],
                    "unitPrice": item['unit_price'],
                    "sizeType": item['sizeType'],
                    "productId": item['product_id'],
                    "orderId": item['order_id'],
                    "rate": True if item['rate'] == 1 else False
                })
            return orderItemList
        except Exception as e:
            print("error: ", str(e))
            return []
    
    
    
    def get_order_by_user(self, userId):
        try:
            orderStatus = request.args.get("orderStatus")
            query = """
                SELECT ord.*, ur.full_name FROM orders ord  
                LEFT JOIN users ur
                ON ord.user_id = ur.id
                WHERE ord.user_id = %s AND ord.status = %s
            """
            
            self.cur.execute(query, (userId, orderStatus))
            results = self.cur.fetchall()
            self.con.commit()
            time.sleep(0.5)
            orderList = []
            
            for item in results:
                
                orderList.append({
                    "id" : item['id'],
                    "orderDate": item['order_date'],
                    "orderStatus": item['status'],
                    "paymentMethod": item['payment_method'],
                    "name": item['full_name'],
                    "shippingAddress": item['shipping_address'],
                    "phoneNumber": item['phone_number'],
                    "note": item['note'],
                    "totalPayment": item['total_amount'],
                    "totalProductAmount": item['totalProductAmount'],
                    "shippingFee": item['shippingFee'],
                    "discountAmount": item['discount_amount'],
                    "discountShippingFee": item['discountShippingFee'],
                    "orderItems": self.get_list_order_item(item['id']),
                    "userId": item['user_id'],
                    "urlPayment": item['urlPayment']
                })
            json = {
                 "content":orderList
            }
            return jsonify(json)
        except Exception as e:
            print("error: ", str(e))
            return jsonify("msg: ", str(e)) , 500

    def create_payment(self, totalAmount, orderId):
        vnp_TxnRef = orderId
        # vnp_TxnRef = generate_random_string(6)
        
        vnp_OrderInfo = 'Thanh toan don hang'
        vnp_OrderType = 'billpayment'
        vnp_Amount = int(totalAmount * 100)  
        vnp_Locale = 'vn'
        vnp_IpAddr = request.remote_addr

        # Tạo ngày giờ hiện tại theo múi giờ "Etc/GMT+7"
        cld = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        vnp_CreateDate = cld.strftime("%Y%m%d%H%M%S")
        cld += datetime.timedelta(minutes=0.2)
        vnp_ExpireDate = cld.strftime("%Y%m%d%H%M%S")

        inputData = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': vnp_TmnCode,
            'vnp_Amount': vnp_Amount,
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': vnp_TxnRef,
            'vnp_OrderInfo': vnp_OrderInfo,
            'vnp_OrderType': vnp_OrderType,
            'vnp_Locale': vnp_Locale,
            'vnp_ReturnUrl': vnp_ReturnUrl,
            'vnp_IpAddr': vnp_IpAddr,
            'vnp_CreateDate': vnp_CreateDate,
            'vnp_ExpireDate': vnp_ExpireDate
        }

        sortedInputData = sorted(inputData.items())
        queryString = urllib.parse.urlencode(sortedInputData)

        hashData = '&'.join([f'{k}={urllib.parse.quote_plus(str(v))}' for k, v in sortedInputData])
        vnp_SecureHash = hmac_sha512(vnp_HashSecret, hashData)

        paymentUrl = f"{vnp_Url}?{queryString}&vnp_SecureHashType=HMACSHA512&vnp_SecureHash={vnp_SecureHash}"

        return paymentUrl

    def get_order_detail(self, orderId):
        try:
            query = f"""
                SELECT ord.*, ur.full_name FROM orders ord  
                LEFT JOIN users ur
                ON ord.user_id = ur.id
                WHERE ord.id = '{orderId}'
            """
            self.cur.execute(query)
            print("query: ", query)
            item = self.cur.fetchone()
            self.con.commit()
            print(item)
            orderDetail = {
                    "id" : item['id'],
                    "orderDate": item['order_date'],
                    "orderStatus": item['status'],
                    "paymentMethod": item['payment_method'],
                    "name": item['full_name'],
                    "shippingAddress": item['shipping_address'],
                    "phoneNumber": item['phone_number'],
                    "note": item['note'],
                    "totalPayment": item['total_amount'],
                    "totalProductAmount": item['totalProductAmount'],
                    "shippingFee": item['shippingFee'],
                    "discountAmount": item['discount_amount'],
                    "discountShippingFee": item['discountShippingFee'],
                    "orderItems": self.get_list_order_item(item['id']),
                    "userId": item['user_id'],
                    "urlPayment": item['urlPayment']
                }
            return jsonify(orderDetail)
        except Exception as e:
            print("error111111: ", str(e))
            return jsonify("msg: ", str(e)) , 500
        
    def update_quantity_item(self, quantity, productId, sizeType):
        try:
            query = f"""
                UPDATE product_size 
                SET quantity = quantity + {quantity},
                    quantity_sold = quantity_sold - {quantity}
                WHERE product_id = {productId} 
                AND size_id = (
                    SELECT id FROM sizes WHERE name = '{sizeType}'
                )
            """
            self.cur.execute(query)
            self.con.commit()
            return True
        except Exception as e:
            print("Error updating item quantity:", str(e))
            return False
        
    def cancel_order(self, orderId):
        try:
            status = request.args.get("orderStatus")
            list_order_item = self.get_list_order_item(orderId)

            for item in list_order_item: 
                quantity = item['quantity']
                productId = item['productId']
                sizeType = item['sizeType']
                
                isCheck = self.update_quantity_item(quantity,productId,sizeType)
                
                if isCheck == False:
                    continue
            
            query = """
                UPDATE orders 
                SET status = %s
                WHERE id = %s
            """
            self.cur.execute(query, (status, orderId))
            self.con.commit()
            return self.get_order_detail(orderId)
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "msg": str(e)
            })
    def get_order_received(self,userId):
        try:
            isRate = request.args.get("isRate")
            rate= 1 if isRate == "true" else 0
            query = f"""
                    SELECT order_items.*
                    FROM order_items
                    JOIN orders ON order_items.order_id = orders.id
                    WHERE orders.status = 'DELIVERED' 
                    and order_items.rate = {rate} 
                    and orders.user_id = {userId};
                    """
            self.cur.execute(query)
            items = self.cur.fetchall()
            self.con.commit()
            count = len(items)
            print(count)
            orderItemList = []
            for item in items:
                orderItemList.append({
                    "id" : item['id'],
                    "quantity": item['quantity'],
                    "unitPrice": item['unit_price'],
                    "sizeType": item['sizeType'],
                    "productId": item['product_id'],
                    "orderId": item['order_id'],
                    "rate": True if item['rate'] == 1 else False
                })
            print(orderItemList)
            return jsonify({
                "content": orderItemList,
                "numberOfElements": int(count)
            }),200

        except Exception as e:
            print(e)
            return jsonify({
                "msg": str(e)
            }),400


    def send_comment(self):
        try:
            product_id = request.args.get('productId')
            rate = int(request.args.get('rate'))
            userId = request.args.get('userId')
            content = request.args.get('content')
            orderItemId = int(request.args.get('orderItemId'))

            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            query_into_comment = f"""
                        INSERT INTO comments (product_id,rate,user_id, create_at, content) 
                                    VALUES ({product_id}, {rate}, {userId},'{formatted_datetime}', '{content}')
                    """
            query_set_orderItem = f"""
                                    UPDATE order_items 
                                    SET rate = 1
                                    WHERE id = {orderItemId}
                                    """
            self.cur.execute(query_into_comment)
            self.con.commit()
            self.cur.execute(query_set_orderItem)
            self.con.commit()
            print(query_into_comment)
            print(query_set_orderItem)
            return jsonify({
                "msg": "Đã gửi đánh giá thành công!"
            }),201
        except Exception as e:
            return  jsonify({
                "msg": e
            }) , 500
    
    def revenue_statistic_year(self):
        try:
            year = request.args.get('year')
            query = """
                SELECT 
                    EXTRACT(MONTH FROM order_date) as month,
                    SUM(total_amount) as revenue
                FROM orders
                WHERE EXTRACT(YEAR FROM order_date) = %s
                GROUP BY EXTRACT(MONTH FROM order_date)
                ORDER BY month
            """
            self.cur.execute(query, (year,))
            results = self.cur.fetchall()
            revenue_data = [{"month": int(result['month']), "revenue": float(result['revenue'])} for result in results]

            self.con.commit()    
            return jsonify(revenue_data) , 200
        
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "msg" : str(e)
            }) , 500
        
    def get_year_order(self):
        try:
            query = """
                SELECT 
                    extract(YEAR FROM order_date) as years
                FROM orders
                GROUP BY extract(YEAR FROM order_date)
                ORDER BY years 
            """
            self.cur.execute(query)
            results = self.cur.fetchall()
            self.con.commit()

            years = [result['years'] for result in results]
            return jsonify(years)            
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "msg": str(e)
            }) , 500
            
    def get_status_order(self):
        try:
            year = request.args.get('year')
            query = """
                SELECT 
                status,
                count(status) as count
                FROM orders
                WHERE EXTRACT(YEAR FROM order_date) = %s
                GROUP BY status
            """
            self.cur.execute(query,(year,))
            results = self.cur.fetchall()
            
            statusList = {result['status'] : result['count'] for result in results}
            self.con.commit()
            return jsonify(statusList)
        except Exception as e:
            print("error: ", str(e))
            return jsonify({
                "msg": str(e)
            }) , 500

