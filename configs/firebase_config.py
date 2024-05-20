import firebase_admin
from firebase_admin import credentials, storage

if not firebase_admin._apps:
    cred = credentials.Certificate("demo1-55087-firebase-adminsdk-avom5-fc97a6fb42.json")
    default_app = firebase_admin.initialize_app(cred, {
        'storageBucket': 'demo1-55087.appspot.com'
    })


bucket = storage.bucket()

def get_bucket():
    return bucket
