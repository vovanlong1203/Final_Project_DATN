from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig

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
    
    
class ProductSizeModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_data(self):
        query = """
            SELECT product_size.id as id, 
            products.name as product,
            product_size.quantity as quantity,
            product_size.quantity_sold as quantity_sold,
            products.status as status,
            sizes.name as size
            FROM product_size 
            LEFT JOIN products on product_size.product_id = products.id
            LEFT JOIN sizes on product_size.size_id = sizes.id
            """
        self.cur.execute(query)
        results = self.cur.fetchall()
        list_product_size = []
        
        for result in results:
            item = {
                'id' : result['id'],
                'product' : result['product'],
                'quantity' : result['quantity'],
                'quantity_sold' : result['quantity_sold'],
                'status' : result['status'],
                'size' : result['size']
            }
            list_product_size.append(item)
        self.con.commit()
        return jsonify(list_product_size), 200
        
    def add_data(self, data):
        print("data: ", data)
        try:            
            query = f"""
                    SELECT * FROM product_size 
                    WHERE product_id = {data['product']} and size_id = {data['size']}
                    """
            self.cur.execute(query)
            
            # Consume the result
            result = self.cur.fetchone()
            
            if result:
                query_insert = f"""
                    UPDATE product_size 
                    SET quantity = quantity + {data['quantity']}
                    WHERE product_id = {data['product']} and size_id = {data['size']}
                """
                msg = "update quantity successfully"
            else:
                query_insert = f"""
                    INSERT INTO product_size(product_id, quantity, quantity_sold, size_id) 
                    VALUES ({data['product']}, {data['quantity']}, 0, {data['size']})
                """
                msg = "insert successfully"
            
            self.cur.execute(query_insert)
            self.con.commit()
            
            return jsonify({
                "msg": msg
            })
            
        except Exception as e:
            print("error: ", e)
            return jsonify({"msg": str(e)})

        
        