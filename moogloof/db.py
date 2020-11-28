from pymongo import MongoClient

from moogloof.config import MONGO_URI


# Fetch db
client = MongoClient(MONGO_URI)
db = client.moogloof
posts = db.posts

