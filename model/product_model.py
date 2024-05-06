from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from typing import List
from datetime import date

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
    
class ProductDetail:
    def __init__(self,
                 product_id=None,
                 product_name=None,
                 price=None,
                 quantity=None,
                 quantity_sold=None,
                 description=None,
                 product_urls=None,
                 comment_created_ats=None,
                 comment_contents=None,
                 comment_users=None,
                 avatar_users=None,
                 size_types=None,
                 size_names=None,
                 size_quantity=None,
                 rate=None,
                 avg_rate=None
                ):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.quantity_sold = quantity_sold
        self.description = description
        self.product_urls = product_urls if product_urls is not None else []
        self.comment_created_ats = comment_created_ats if comment_created_ats is not None else []
        self.comment_contents = comment_contents if comment_contents is not None else []
        self.comment_users = comment_users if comment_users is not None else []
        self.avatar_users = avatar_users if avatar_users is not None else []
        self.size_types = size_types if size_types is not None else []
        self.size_names = size_names if size_names is not None else []
        self.size_quantity = size_quantity if size_quantity is not None else []
        self.rate = rate if rate is not None else []
        self.avg_rate = avg_rate

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'quantity': self.quantity,
            'quantity_sold': self.quantity_sold,
            'description': self.description,
            'product_urls': self.product_urls,
            'comment_created_ats': self.comment_created_ats,
            'comment_contents': self.comment_contents,
            'comment_users': self.comment_users,
            'avatar_users': self.avatar_users,
            'size_types': self.size_types,
            'size_names': self.size_names,
            'size_quantity': self.size_quantity,
            'rate': self.rate,
            'avg_rate': self.avg_rate
            
        }

    @classmethod
    def from_database_result(cls, result):
        if result:
            product_image = result[0]['Link_anh'].split(',') if result[0]['Link_anh'] is not None else []
            rate_list_integer = [int(rate) for rate in result[0]['star'].split(',')] if result[0]['star'] else []

            # Tính toán avg_rate
            avg_rate = sum(rate_list_integer) / len(rate_list_integer) if rate_list_integer else 0.0

            product_detail = cls(
                product_id=result[0]['id'],
                product_name=result[0]['name'],
                price=result[0]['price'],
                quantity=result[0]['quantity'],
                quantity_sold=result[0]['quantity_sold'],
                description=result[0]['description'],
                product_urls=product_image,
                comment_created_ats=result[0]['ngaytaocmt'].split(',') if result[0]['ngaytaocmt'] else [],
                comment_contents=result[0]['noidungcmt'].split(',') if result[0]['noidungcmt'] else [],
                comment_users=result[0]['nguoicmt'].split(',') if result[0]['nguoicmt'] else [],
                avatar_users=result[0]['Avatar'].split(',') if result[0]['Avatar'] else [],
                size_types=result[0]['loai_size'].split(',') if result[0]['loai_size'] else [],
                size_names=result[0]['ten_size'].split(',') if result[0]['ten_size'] else [],
                size_quantity=result[0]['SoLuongConLai'].split(',') if result[0]['SoLuongConLai'] else [],
                rate=rate_list_integer,
                avg_rate=avg_rate  # Gán avg_rate vào đây
            )
            return product_detail
        return None



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


    def get_product_detail(self):
        try:
            con = connect_to_database()
            cur = con.cursor(dictionary=True)

            pr_id = request.args.get("pr_id")
            cur.execute("""            
            WITH 
            AnhSanPham AS (
                SELECT
                    pr.*,
                    GROUP_CONCAT(pi.url) AS Link_anh
                FROM
                    products pr
                LEFT JOIN
                    product_images pi ON pi.product_id = pr.id
                GROUP BY
                    pr.id
            ),
            Sizes AS (
                SELECT
                    GROUP_CONCAT(ps.quantity) AS SoLuongConLai,
                    pr.id AS Id_sp,
                    GROUP_CONCAT(s.id) AS loai_size,
                    GROUP_CONCAT(s.name) AS ten_size
                FROM
                    product_size ps
                LEFT JOIN
                    products pr ON pr.id = ps.product_id
                LEFT JOIN
                    sizes s ON s.id = ps.size_id
                GROUP BY
                    pr.id
            ),
            CMT_US AS (
                SELECT
                    GROUP_CONCAT(cmt.content) AS noidungcmt,
                    GROUP_CONCAT(cmt.create_at) AS ngaytaocmt,
                    GROUP_CONCAT(us.full_name) AS nguoicmt,
                    GROUP_CONCAT(us.url_image) AS Avatar,
                    pr.id AS idsp,
                    pr.name,
                    GROUP_CONCAT(cmt.rate) AS star
                FROM
                    products pr
                LEFT JOIN
                    comments cmt ON pr.id = cmt.product_id
                LEFT JOIN
                    users us ON us.id = cmt.user_id
                GROUP BY
                    pr.id
            )
            SELECT
                ct.id AS Loai_san_pham,
                ct.name AS Ten_loai_san_pham,
                pr.id,
                pr.name,
                pr.price,
                SUM(psi.quantity) AS quantity,
                SUM(psi.quantity_sold) AS quantity_sold,
                pr.description,
                Link_anh,
                ngaytaocmt,
                noidungcmt,
                nguoicmt,
                Avatar,
                loai_size,
                ten_size,
                SoLuongConLai,
                star
        
            FROM
                products pr
            JOIN
                categories ct ON ct.id = pr.category_id
            LEFT JOIN
                product_size psi ON psi.product_id = pr.id
            LEFT JOIN
                AnhSanPham asp ON pr.id = asp.id
            JOIN
                Sizes siz ON siz.Id_sp = pr.id
            LEFT JOIN
                CMT_US ON pr.id = CMT_US.idsp
            WHERE
                pr.id = %s AND pr.is_deleted != 1
            GROUP BY
                pr.id;

            """, (pr_id,))

            result = cur.fetchall()
            product_detail = ProductDetail.from_database_result(result)

            if product_detail:
                return jsonify(product_detail.to_dict())
            else:
                return jsonify({"message": "Product not found"})
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
        finally:
            if con:
                con.close()