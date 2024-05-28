from flask import Flask, request
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, create_access_token, set_access_cookies
from datetime import datetime, timedelta
from flask_cors import CORS

app =  Flask(__name__)
CORS(app, resources={r"*": {"origins": "https://admin-final-project-react-o57jud3ue-vanlongs-projects.vercel.app"}})

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = '09775b945044532aea6b56d06884b7df'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['CORS_HEADERS'] = 'Content-Type'

jwt = JWTManager(app)

try:
    from controller import *
except Exception as e:
    print(e)

if __name__ == '__main__':
     app.run(host='0.0.0.0')
    
