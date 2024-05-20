from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta

app =  Flask(__name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = '09775b945044532aea6b56d06884b7df'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)

try:
    from controller import *
except Exception as e:
    print(e)

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0', port=8080)
    
