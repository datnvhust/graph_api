from django.conf import settings
from pymongo import MongoClient


def db_connect():
    client = MongoClient(settings.MONGODB_HOST, settings.MONGODB_PORT)
    client.admin.authenticate(settings.MONGODB_USERNAME, settings.MONGODB_PASSWORD)
    db = client[settings.MONGODB_NAME]
    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['mydatabase']
    return db


def get_collection(collection):
    db = db_connect()
    return db[collection]
