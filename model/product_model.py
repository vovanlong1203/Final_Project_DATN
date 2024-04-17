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

class Product:
    def __init__(self, product_id=None, product_name=None, price=None, quantity=None, quantity_sold=None, product_image=None, category_id=None, category_name=None):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.quantity_sold = quantity_sold
        self.product_image = product_image
        self.category_id = category_id
        self.category_name = category_name

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'quantity': self.quantity,
            'quantity_sold': self.quantity_sold,
            'product_image': self.product_image,
            'category_id': self.category_id,
            'category_name': self.category_name
        }

class ProductModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
            print("OKE")
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")

    def get_all_products(self):
        try:
            self.cur.execute("""
            WITH AnhSanPham AS (
                SELECT
                    pr.*,
                    GROUP_CONCAT(pi.url) AS Link_anh
                FROM
                    products pr
                JOIN product_images pi ON pi.product_id = pr.id
                GROUP BY
                    pr.id
            )
            SELECT
                pr.id,
                pr.name,
                pr.price,
                SUM(psi.quantity) AS quantity,
                SUM(psi.quantity_sold) AS quantity_sold,
                Link_anh,
                pr.category_id AS category_id,
                ct.name AS category_name

            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id
            WHERE
                pr.is_deleted != TRUE
            GROUP BY
                pr.id;
            """)
            results = self.cur.fetchall()
            products = []
            for result in results:
                product_image = result['Link_anh'].split(',') if result['Link_anh'] is not None else []
                product = Product(
                    product_id=result['id'],
                    product_name=result['name'],
                    price=result['price'],
                    quantity=result['quantity'],
                    quantity_sold=result['quantity_sold'],
                    product_image=product_image, 
                    category_id=result['category_id'],
                    category_name=result['category_name']
                )
                products.append(product.to_dict())
            return jsonify(products)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
        finally:
            if self.con:
                self.con.close()




    def search_products(self):
        try:
            con = connect_to_database()
            cur = con.cursor(dictionary=True)

            keyword = request.args.get("keyword")
            min_price = request.args.get("min_price")
            max_price = request.args.get("max_price")
            category = request.args.get("category")
            if min_price =="" :
                min_price = 0
            if max_price =="":
                max_price = 99999999999999

    
            cur.execute("""
            WITH AnhSanPham AS (
                SELECT
                    pr.*,
                    GROUP_CONCAT(pi.url) AS Link_anh
                FROM
                    products pr
                LEFT JOIN
                    product_images pi ON pi.product_id = pr.id
                GROUP BY
                    pr.id
            )
            SELECT
                pr.id,
                pr.name,
                pr.price,
                SUM(psi.quantity) AS quantity,
                SUM(psi.quantity_sold) AS quantity_sold,
                Link_anh,
                pr.category_id AS category_id,
                ct.name AS category_name
            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id
            WHERE
                pr.is_deleted != TRUE 
                AND pr.name LIKE %s
                AND pr.price BETWEEN %s AND %s
                AND ct.name LIKE %s
            GROUP BY
                pr.id;
            """, (f"%{keyword}%", min_price, max_price, f"%{category}%"))

            results = cur.fetchall()
            products = []
            for result in results:
                product_image = result['Link_anh'].split(',') if result['Link_anh'] is not None else []
                product = Product(
                    product_id=result['id'],
                    product_name=result['name'],
                    price=result['price'],
                    quantity=result['quantity'],
                    quantity_sold=result['quantity_sold'],
                    product_image=product_image,
                    category_id=result['category_id'],
                    category_name=result['category_name']
                )
                products.append(product.to_dict())

            return jsonify(products)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
        finally:
            if con:
                con.close()
