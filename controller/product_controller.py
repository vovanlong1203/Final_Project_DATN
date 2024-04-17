from app import app
from model.product_model import ProductModel
product_model = ProductModel()


@app.route("/products/all")
def get_all_products():
    return product_model.get_all_products()