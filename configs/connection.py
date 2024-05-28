import mysql.connector
from configs.config import dbconfig

def connect_to_database():
    try:
        con = mysql.connector.connect(
                    host = dbconfig["host"],
                    port = dbconfig["port"],
                    user = dbconfig["username"],
                    password = dbconfig["password"],
                    database = dbconfig["database"])
        return con
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối đến cơ sở dữ liệu: {err}")
        return None