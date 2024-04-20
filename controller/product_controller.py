from app import app
from model.product_model import ProductModel
product_model = ProductModel()


@app.route("/products/all", methods=["GET"])
def get_all_products():
    return product_model.get_all_products()

@app.route("/products/search", methods=["GET"])
def search_products():
    return product_model.search_products()

@app.route("/products/product_detail", methods=["GET"])
def get_product_detail():
    return product_model.get_product_detail()