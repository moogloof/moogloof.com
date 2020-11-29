from pymongo import MongoClient
from flask import g

from moogloof.app import app
from moogloof.config import MONGO_URI


# Fetch db
def get_db():
	if 'db' not in g:
		g.db = MongoClient(MONGO_URI)

	return g.db

# Close db
@app.teardown_appcontext
def teardown_db(e):
	db = g.pop('db', None)

	if db is not None:
		db.close()

