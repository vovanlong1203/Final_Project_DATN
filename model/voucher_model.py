from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
from datetime import datetime
from datetime import datetime
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
    
class DiscountType(Enum):
    amount = 'AMOUNT'
    percentage = 'PERCENTAGE'

class VoucherType(Enum):
    purchase = 'PURCHASE'
    freeship = 'PREE_SHIP'
    

class Voucher:
    def __init__(self, id=None, minimum_purchase_amount=None, usage_count=None, usage_limit=None, voucher_value=None, end_at=None, start_at=None, code=None, discount_type=None, voucher_type = None,maxDiscountValue = None, active=None):
        self.id = id
        self.minimum_purchase_amount = minimum_purchase_amount
        self.usage_count = usage_count
        self.usage_limit = usage_limit
        self.voucher_value = voucher_value
        self.end_at = end_at
        self.start_at = start_at
        self.code = code
        self.discount_type = discount_type
        self.voucher_type = voucher_type
        self.maxDiscountValue = maxDiscountValue
        self.active = active
        
    def to_dict_mobile(self):
        return {
            'id': self.id,
            'minimumPurchaseAmount': self.minimum_purchase_amount,
            'usageCount': self.usage_count,
            'usageLimit': self.usage_limit,
            'discountValue': self.voucher_value,
            'expiryDate': self.end_at.strftime('%H:%M:%S %d-%m-%Y'),
            'expiryDate': self.end_at.strftime('%H:%M:%S %d-%m-%Y'),
            'start_at': self.start_at,
            'code': self.code,
            'discountType': self.discount_type,
            'voucherType' : self.voucher_type,
            'active' : bool(self.active) ,
            'maxDiscountValue' : self.maxDiscountValue
        }
    def to_dict(self):
        return{
            'id': self.id,
            'minimum_purchase_amount': self.minimum_purchase_amount,
            'usage_count': self.usage_count,
            'usage_limit': self.usage_limit,
            'voucher_value': self.voucher_value,
            'end_at': self.end_at,
            'start_at': self.start_at,
            'code': self.code,
            'discount_type': self.discount_type,
            'voucher_type' : self.voucher_type
        }
        
class VoucherModel:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def get_all(self):
        try: 
            query = f"SELECT * FROM vouchers"
            self.cur.execute(query)
            
            results = self.cur.fetchall()
            
            list_voucher = []
            for result in results:
                voucher = Voucher(id=result['id'],
                                  minimum_purchase_amount=result['minimum_purchase_amount'],
                                  usage_count=result['usage_count'],
                                  usage_limit=result['usage_limit'],
                                  voucher_value=result['voucher_value'],
                                  end_at=result['end_at'],
                                  start_at=result['start_at'],
                                  code=result['code'],
                                  discount_type=result['discount_type']
                                )
                list_voucher.append(voucher.to_dict())
            self.con.commit()
            print('list_promotion: ',list_voucher)
            return jsonify(list_voucher), 200
            
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
            
    def add_voucher(self, data):
        try:
            query = f"""
                INSERT INTO vouchers (minimum_purchase_amount, usage_count, usage_limit, voucher_value, end_at, start_at, code, discount_type)
                VALUES ({data['minimum_purchase_amount']}, {data['usage_count']}, {data['usage_limit']}, {data['voucher_value']}, '{data['end_at']}', '{data['start_at']}', '{data['code']}', '{data['discount_type']}')
            """
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "insert promotion successfully"
            })
            
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
            
    def update_voucher(self, voucher_id, data):
        try:
            query = f"""
                UPDATE vouchers
                SET minimum_purchase_amount = {data['minimum_purchase_amount']},
                    usage_count = {data['usage_count']},
                    usage_limit = {data['usage_limit']},
                    voucher_value = {data['voucher_value']},
                    end_at = '{data['end_at']}',
                    start_at = '{data['start_at']}',
                    code = '{data['code']}',
                    discount_type = {data['discount_type']}
                WHERE id = {voucher_id}
            """
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "update promotion successfully"
            })
            
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })

    def delete_voucher(self, voucher_id):
        try:
            query = f"""
                DELETE FROM vouchers
                WHERE id = {voucher_id}
            """
            self.cur.execute(query)
            self.con.commit()
            
            return jsonify({
                "message": "delete promotion successfully"
            })
            
        except Exception as e:
            print("error: ", e)
            return jsonify({
                "msg": e
            })
        
    def get_voucher_by_type(self):
        try:
            voucherType = request.args.get("voucherType")
            query = f"""SELECT * FROM vouchers WHERE voucher_type = '{voucherType}' and active = 1"""
            self.cur.execute(query)
            results = self.cur.fetchall()
            vouchers = []
            for result in results:
                voucher =Voucher(
                    id=result['id'],
                    minimum_purchase_amount=result['minimum_purchase_amount'],
                    minimum_purchase_amount=result['minimum_purchase_amount'],
                    usage_count=result['usage_count'],
                    usage_limit=result['usage_limit'],
                    voucher_value=result['voucher_value'],
                    end_at=result['end_at'],
                    start_at=result['start_at'],
                    code=result['code'],
                    discount_type=result['discount_type'],
                    discount_type=result['discount_type'],
                    voucher_type=result['voucher_type'],
                    maxDiscountValue=result['maxDiscountValue'],
                    active= result['active']
                    maxDiscountValue=result['maxDiscountValue'],
                    active= result['active']
                )
                vouchers.append(voucher.to_dict_mobile())
            return jsonify({
                "content":vouchers

            }),200
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")