from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from configs.connection import connect_to_database
    
    
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

    def search_product_size_admin(self):
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            offset = (page - 1) * limit
            keyword = request.args.get('keyword', '').lower()  # Lấy keyword từ query parameters
            
            if keyword is not None:
                search_query = """
                    SELECT product_size.id as id, 
                        products.name as product,
                        product_size.quantity as quantity,
                        product_size.quantity_sold as quantity_sold,
                        products.status as status,
                        sizes.name as size
                    FROM product_size 
                    LEFT JOIN products ON product_size.product_id = products.id
                    LEFT JOIN sizes ON product_size.size_id = sizes.id
                    WHERE LOWER(products.name) LIKE %s
                    LIMIT %s OFFSET %s
                """
                search_keyword = f"%{keyword}%"
                self.cur.execute(search_query, (search_keyword, limit, offset))
            else:
                # Câu truy vấn chính để lấy dữ liệu sản phẩm với phân trang
                query = """
                    SELECT product_size.id as id, 
                        products.name as product,
                        product_size.quantity as quantity,
                        product_size.quantity_sold as quantity_sold,
                        products.status as status,
                        sizes.name as size
                    FROM product_size 
                    LEFT JOIN products ON product_size.product_id = products.id
                    LEFT JOIN sizes ON product_size.size_id = sizes.id
                    LIMIT %s OFFSET %s
                """
                self.cur.execute(query, (limit, offset))
            
            results = self.cur.fetchall()
            self.con.commit()
            list_product_size = []
            for result in results:
                item = {
                    'id': result['id'],
                    'product': result['product'],
                    'quantity': result['quantity'],
                    'quantity_sold': result['quantity_sold'],
                    'status': result['status'],
                    'size': result['size']
                }
                list_product_size.append(item)
            
            if keyword is not None:
                count_query = """
                    SELECT COUNT(*) as total
                    FROM product_size 
                    LEFT JOIN products ON product_size.product_id = products.id
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
            total_pages = (total_items + limit - 1) // limit  # Tính tổng số trang
            
            self.con.commit()

            response = {
                'items': list_product_size,
                'totalPages': total_pages,
            }
            
            return jsonify(response), 200
        except Exception as e:
            print("Error:", str(e))
            return jsonify({"msg": str(e)}), 500
        
        