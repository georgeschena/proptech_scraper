from flask import Flask, escape, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.property_model import Properties
import os

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')


@app.route('/all_properties')
def get_all_properties():
    return jsonify(
        {
            "count": Properties.query.count(),
            "properties": list(map(lambda prop: prop.serialize(), Properties.query.all()))
        })
