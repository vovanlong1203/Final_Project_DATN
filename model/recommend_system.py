from flask import jsonify,request
import mysql.connector
from configs.config import dbconfig
from enum import Enum
import datetime
from datetime import timezone
from datetime import timedelta
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from werkzeug.utils import secure_filename
from configs.connection import connect_to_database
import time

class Recommend_System:
    def __init__(self):
        try:
            self.con = connect_to_database()
            self.cur = self.con.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    def predict_rating(self,user_index, product_index, similarity_matrix, ratings, num_users):
        rated_product_indices = np.where(ratings[user_index, :] != 0)[0]
        
        if len(rated_product_indices) == 0:
            return 0
        
        weights = np.array([similarity_matrix[user_index, i] for i in range(num_users) if i != user_index])
        ratings_of_product = np.array([ratings[i, product_index] for i in range(num_users) if i != user_index])
        
        if np.sum(weights) == 0:
            return 0
        
        predicted_rating = np.dot(weights, ratings_of_product) / np.sum(weights)
        
        return predicted_rating

    def recommend_products(self, user_id, similarity_matrix, ratings, unique_user_ids , unique_product_ids, num_users,  num_recommendations=5):
        user_index = unique_user_ids.index(user_id)
        recommendations = []
        
        for i, product_id in enumerate(unique_product_ids):
            if ratings[user_index, i] == 0:
                predicted_rating = self.predict_rating(user_index, i, similarity_matrix, ratings, num_users)
                if predicted_rating > 0:
                    recommendations.append((product_id, predicted_rating))
        
        if len(recommendations) < num_recommendations:
            ratings_array = np.array(ratings)
            max_ratings = np.max(ratings_array, axis=0)
            max_ratings_indices = np.argsort(max_ratings)[::-1]
            for i in max_ratings_indices[:num_recommendations - len(recommendations)]:
                recommendations.append((unique_product_ids[i], ratings_array[unique_user_ids != user_id, i].mean()))
        
        recommendations.sort(key=lambda x: x[1], reverse=True) 
        list = [product_id for product_id, _ in recommendations[:num_recommendations]]
        print("list: ", list)
        return list
    
    
    
    def get_list_product(self, userId):
        try:
            print("user_id: ", userId)
            query = "SELECT user_id, product_id, rate FROM comments"
            self.cur.execute(query)
            result = self.cur.fetchall()
            self.con.commit()
            time.sleep(0.2)
            # Convert result to pandas DataFrame
            columns = ['user_id', 'product_id', 'rate']
            data = pd.DataFrame(result, columns=columns)
            
            print("data: ", data)
            
            unique_user_ids = list(set(data['user_id']))
            unique_product_ids = list(set(data['product_id']))
            print("unique_user_ids: ", unique_user_ids)
            print("unique_product_ids: ", unique_product_ids)
            num_users = len(unique_user_ids)
            num_products = len(unique_product_ids)
            ratings = np.zeros((num_users, num_products))
            
            for i, user_id in enumerate(unique_user_ids):
                for j, product_id in enumerate(unique_product_ids):
                    rating_index = [k for k in range(len(data['user_id'])) if data['user_id'][k] == user_id and data['product_id'][k] == product_id]
                    if rating_index:
                        ratings[i, j] = data['rate'][rating_index[0]] if rating_index[0] < len(data['rate']) else 0

            similarity_matrix = np.zeros((num_users, num_users))
            
            for i in range(num_users):
                for j in range(num_users):
                    if i!= j:
                        similarity_matrix[i, j] = 1 - cosine(ratings[i, :], ratings[j, :])

            user_index = unique_user_ids.index(userId)
            recommendations = []

            for i, product_id in enumerate(unique_product_ids):
                if ratings[user_index, i] == 0:
                    rated_product_indices = np.where(ratings[user_index, :]!= 0)[0]
                    if len(rated_product_indices) == 0:
                        continue
                    weights = np.array([similarity_matrix[user_index, k] for k in range(num_users) if k!= user_index])
                    ratings_of_product = np.array([ratings[k, i] for k in range(num_users) if k!= user_index])
                    if np.sum(weights) == 0:
                        continue
                    predicted_rating = np.dot(weights, ratings_of_product) / np.sum(weights)
                    if predicted_rating > 0:
                        recommendations.append((product_id, predicted_rating))
                
                
            if len(recommendations) < 5:
                ratings_array = np.array(ratings)
                max_ratings = np.max(ratings_array, axis=0)
                max_ratings_indices = np.argsort(max_ratings)[::-1]
                for i in max_ratings_indices[:5 - len(recommendations)]:
                    recommendations.append((unique_product_ids[i], ratings_array[unique_user_ids!= user_id, i].mean()))                

            recommendations.sort(key=lambda x: x[1], reverse=True)
            recommended_product_ids = [product_id for product_id, _ in recommendations[:5]]                        
            
            query = """
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
                    pr.is_deleted != TRUE AND pr.id IN (%s)
                GROUP BY
                    pr.id;
            """ % ",".join(map(str, recommended_product_ids))

            self.cur.execute(query)
            results = self.cur.fetchall()
            self.con.commit()
            products = []
            for result in results:
                if result.get('Link_anh'):
                    product_image = result['Link_anh'].split(',')
                else:
                    product_image = []

                products.append({
                    "product_id": result['id'],
                    "product_name": result['name'],
                    'price': result['price'],
                    "price_promote":result['price_promote'],
                    "quantity":result['quantity'],
                    "quantity_sold":result['quantity_sold'],
                    "product_image":product_image,
                    "category_id":result['category_id'],
                    "category_name":result['category_name']
                })
                
            return jsonify({
                "items":products
            })
        except Exception as e:
            print("error: ", str(e))
            
