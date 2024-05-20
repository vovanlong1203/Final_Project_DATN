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
    def __init__(self, product_id=None, product_name=None, price=None, price_promote=None,quantity=None, quantity_sold=None, product_image=None, category_id=None, category_name=None):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.quantity = quantity
        self.quantity_sold = quantity_sold
        self.product_image = product_image
        self.category_id = category_id
        self.category_name = category_name
        self.price_promote = price_promote

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'price_promote': self.price_promote,
            'quantity': self.quantity,
            'quantity_sold': self.quantity_sold,
            'product_image': self.product_image,
            'category_id': self.category_id,
            'category_name': self.category_name


        }
    

class Category:
    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class ProductDetail:
    def __init__(self,
                 product_id=None,
                 product_name=None,
                 price=None,
                 price_promote=None,
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
        self.price_promote =price_promote
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
            'productId': self.product_id,
            'productName': self.product_name,
            'price': self.price,
            "price_promote": self.price_promote,
            'quantity': self.quantity,
            'quantity_sold': self.quantity_sold,
            'description': self.description,
            'productUrls': self.product_urls,
            'commentCreatedAts': self.comment_created_ats,
            'commentContents': self.comment_contents,
            'commentUsers': self.comment_users,
            'avatarUsers': self.avatar_users,
            'sizeTypes': self.size_types,
            'sizeNames': self.size_names,
            'sizeQuantity': self.size_quantity,
            'rate': self.rate,
            'avgRate': self.avg_rate
            
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
                price_promote = result[0]["price_promote"],
                quantity=int(result[0]['quantity']),
                quantity_sold=int(result[0]['quantity_sold']),
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
                ct.name AS category_name,
                CASE 
        WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN pr.price 
        ELSE (pr.price - promotions.discount_value) 
    END AS price_promote 

            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id

            LEFT JOIN promotions 
            ON 
				pr.promotion_id = promotions.id
            WHERE
                pr.is_deleted != TRUE
            GROUP BY
                pr.id;
            """)
            results = self.cur.fetchall()
            self.con.commit()
            products = []
            for result in results:
                if result.get('Link_anh'):
                    product_image = result['Link_anh'].split(',')
                else:
                    product_image = []

                product = Product(
                    product_id=result['id'],
                    product_name=result['name'],
                    price=result['price'],
                    price_promote=result['price_promote'],
                    quantity=result['quantity'],
                    quantity_sold=result['quantity_sold'],
                    product_image=product_image,  # Sử dụng danh sách liên kết hình ảnh
                    category_id=result['category_id'],
                    category_name=result['category_name']
                )

                products.append(product.to_dict())




            # products = []
            # for result in results:
            #     product_image = result['Link_anh'] if result['Link_anh'] is not None else []
            #     product = Product(
            #         product_id=result['id'],
            #         product_name=result['name'],
            #         price=result['price'],
            #         price_promote =result['price_promote'],
            #         quantity=result['quantity'],
            #         quantity_sold=result['quantity_sold'],
            #         product_image=product_image, 
            #         category_id=result['category_id'],
            #         category_name=result['category_name']
            #     )
            #     products.append(product.to_dict())
            return jsonify({
                "items":products
            })
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
    
    def add_product(self, data):
        try:
            if 'promotion' in data and data['promotion'] == "null":
                query = "INSERT INTO products (name, description, create_at, update_at, price, category_id, status, promotion_id) \
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, NULL)"
                values = (data['name'], data['description'], data['price'], data['category'], data['status'])
            else:
                query = "INSERT INTO products (name, description, create_at, update_at, price, category_id, status, promotion_id) \
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s)"
                values = (data['name'], data['description'], data['price'], data['category'], data['status'], data['promotion'])

            self.cur.execute(query, values)
            self.con.commit()

            return jsonify({
                "msg": "successfully"
            })

        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": str(e)
            })
         
    def get_product(self):
        try: 
            query = """
                SELECT 
                    products.id as id, 
                    products.name as name, 
                    products.description as description,
                    products.status as status, 
                    products.price as price, 
                    categories.name as category, 
                    IF(promotions.end_at < NOW(), NULL, promotions.name) AS promotion
                FROM 
                    products
                LEFT JOIN 
                    categories on products.category_id = categories.id
                LEFT JOIN 
                    promotions on products.promotion_id = promotions.id
            """
                        
            self.cur.execute(query)
            result = self.cur.fetchall()
            print("result: ", result)
            lst = []
            for item in result:
                lst.append({
                    'id': item['id'],
                    'name': item['name'],
                    'description': item['description'],
                    'status': item['status'],
                    'price': item['price'],
                    'category': item['category'],
                    'promotion': item['promotion']
                })
            self.con.commit()
            return jsonify(lst)
        except Exception as e:
            print("error: ", e)
            return jsonify({"msg": str(e)}) 
    
    def update_product(self, new_data):
        try:
            query = f"""
                UPDATE products
                SET 
                    name = '{new_data.get('name')}',
                    description = '{new_data.get('description')}',
                    status = '{new_data.get('status')}',
                    price = {new_data.get('price')},
                    category_id = (SELECT id FROM categories WHERE name = '{new_data.get('category')}'),
                    promotion_id = (
                        CASE 
                            WHEN '{new_data.get('promotion')}' IS NULL THEN NULL 
                            WHEN '{new_data.get('promotion')}' = 'null' THEN NULL 
                            ELSE (SELECT id FROM promotions WHERE name = '{new_data.get('promotion')}')
                        END
                    )
                WHERE
                    id = {new_data.get('id')}
            """
            self.cur.execute(query)
            self.con.commit()
            return jsonify({"msg": "Product updated successfully"})
        except Exception as e:
            print("error: ", e)
            return jsonify({"msg": str(e)})

    def delete_product(self, id):
        try:
            query = f"""
                        DELETE FROM products WHERE id = {id}
                    """
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "msg": "products deleted successfully"
            })
        except Exception as e:
            print("error: ", e)
            return jsonify({"msg": str(e)})

    def search_products(self):
        try:
            keyword = request.args.get("keyword")
            min_price = request.args.get("min_price")
            max_price = request.args.get("max_price")
            category = request.args.get("category")
            print("key:",keyword,"   min:" ,min_price,"    max:",max_price,"    category:" ,category)
            if min_price ==None and max_price ==None:
                min_price = 0
                max_price = 99999999999999

            if category!=None:
                self.cur.execute("""
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
                ct.name AS category_name,
                CASE 
        WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN pr.price 
        ELSE (pr.price - promotions.discount_value) 
    END AS price_promote
            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id
                                 LEFT JOIN promotions 
            ON 
				pr.promotion_id = promotions.id
            WHERE
                pr.is_deleted != TRUE 
                AND pr.price BETWEEN %s AND %s
                AND ct.name LIKE %s
            GROUP BY
                pr.id;
            """, ( min_price, max_price, f"%{category}%"))
            if keyword!=None:
                self.cur.execute("""
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
                ct.name AS category_name,
                                 CASE 
        WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN pr.price 
        ELSE (pr.price - promotions.discount_value) 
    END AS price_promote
            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id
            LEFT JOIN promotions 
            ON 
				pr.promotion_id = promotions.id
            WHERE
                pr.is_deleted != TRUE 
                AND pr.name LIKE %s
                AND pr.price BETWEEN %s AND %s
            GROUP BY
                pr.id;
            """, (f"%{keyword}%", min_price, max_price))
            if keyword == None and category == None:
                self.cur.execute("""
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
                ct.name AS category_name,
                                 CASE 
        WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN pr.price 
        ELSE (pr.price - promotions.discount_value) 
    END AS price_promote
            FROM
                products pr
            LEFT JOIN AnhSanPham asp ON asp.id = pr.id
            LEFT JOIN categories ct ON ct.id = pr.category_id
            LEFT JOIN product_size psi ON psi.product_id = pr.id
                                 LEFT JOIN promotions 
            ON 
				pr.promotion_id = promotions.id
            WHERE
                pr.is_deleted != TRUE 
                AND pr.price BETWEEN %s AND %s
            GROUP BY
                pr.id;
            """, ( min_price, max_price))

            results = self.cur.fetchall()
            self.con.commit()
            products = []
            for result in results:
                product_image = result['Link_anh'].split(',') if result['Link_anh'] is not None else []
                product = Product(
                    product_id=result['id'],
                    product_name=result['name'],
                    price=result['price'],
                    price_promote=result['price_promote'],
                    quantity=result['quantity'],
                    quantity_sold=result['quantity_sold'],
                    product_image=product_image,
                    category_id=result['category_id'],
                    category_name=result['category_name']
                )
                products.append(product.to_dict())

            return jsonify({"items":products})
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")


    def get_product_detail(self):
        try:
            
            pr_id = request.args.get("id")
            self.cur.execute("""            
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
                 CASE
                    WHEN promotions.discount_value IS NULL OR promotions.is_active = 0 OR promotions.end_at < NOW() THEN pr.price 
        ELSE (pr.price - promotions.discount_value) 
    END AS price_promote ,
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
                LEFT JOIN promotions 
            ON 
				pr.promotion_id = promotions.id
            JOIN
                Sizes siz ON siz.Id_sp = pr.id
            LEFT JOIN
                CMT_US ON pr.id = CMT_US.idsp
            WHERE
                pr.id = %s AND pr.is_deleted != 1
            GROUP BY
                pr.id;
            

            """, (pr_id,))

            result = self.cur.fetchall()
            self.con.commit()
            product_detail = ProductDetail.from_database_result(result)

            if product_detail:
                return jsonify(product_detail.to_dict())
            else:
                return jsonify({"message": "Product not found"})
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")

    
    def get_category_name(self):
        try:
            
            self.cur.execute("""            
           SELECT * FROM categories;
            """, )

            results = self.cur.fetchall()
            self.con.commit()
            categorys = []
            for result in results:
                category = Category(
                    id=result['id'],
                    name=result['name'],
                    description=result['description']
                )
                categorys.append(category.to_dict())
            return jsonify(categorys)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
        

