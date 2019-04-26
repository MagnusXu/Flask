from flask import Flask, render_template, redirect, g, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import requests
import json
from flask_restful import reqparse, abort, Api, Resource

DATABASE = 'todolist.db'

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Item(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	what_to_do = db.Column(db.String(80), unique = True)
	due_date = db.Column(db.String(120), unique = True)

	def __init__(self, what_to_do, due_date):
		self.what_to_do = what_to_do
		self.due_date = due_date

class ItemSchema(ma.Schema):
	class Meta:
		fields = ('what_to_do', 'due_date')

item_schema = ItemSchema()
items_schema = ItemSchema(many = True)

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(app.config['DATABASE'])
	return db

@app.route("/")
def show_list():
	database = get_db()
	url = 'http://localhost:6000/api/items'
	try:
		r = requests.get(url)
		json_dict = json.loads(json.dumps(r.json()))
		return render_template('index.html', todolist = json_dict)
	except:
		raise ApiError('GET /items/ {}'.format(r.statue_code))

# endpoint to create new item
@app.route("/add/item", methods = ['POST'])
def create_item():
	what_to_do = request.json['what_to_do']
	due_date = request.json['due_date']

	new_item = Item(what_to_do, due_date)

	db.session.add(new_item)
	db.session.commit()

	return jsonify(new_item)

# endpoint to show all items
@app.route("/api/item", methods=["GET"])
def get_items():
    all_items = Item.query.all()
    result = items_schema.dump(all_items)
    return jsonify(result.data)

# endpoint to get item detail by id
@app.route("/api/item/<id>", methods=["GET"])
def get_item(id):
    item = Item.query.get(id)
    return item_schema.jsonify(item)

# endpoint to update item
@app.route("/update/item/<id>", methods=["PUT"])
def update_item(id):
    item = Item.query.get(id)
    what_to_do = request.json['what_to_do']
    due_date = request.json['due_date']

    item.due_date = due_date
    item.what_to_do = what_to_do

    db.session.commit()
    return item_schema.jsonify(item)


# endpoint to delete item
@app.route("/delete/item/<id>", methods=["DELETE"])
def item_delete(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()

    return item_schema.jsonify(item)

@app.route('/summary')
def summary():
	data = make_summary
	return jsonify(data)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
