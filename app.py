from flask import Flask, escape, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from property_model import Property
import os

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object('config')

app.config['SQLALCHEMY_DATABASE_URI'] = app.config["SQLALCHEMY_DATABASE_URI"]


@app.route('/all_properties')
def get_all_properties():
    return jsonify(
        {
            "count": Property.query.count(),
            "properties": list(map(lambda prop: prop.serialize(), Property.query.all()))
        })
