from flask import Flask, escape, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from property_model import Property
import os
from datetime import date

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')


@app.route('/all_properties')
def get_all_properties():
    return jsonify(
        {
            "count": Property.query.count(),
            "properties": list(map(lambda prop: prop.serialize(), Property.query.all()))
        })


@app.route('/todays_properties')
def get_todays_properties():
    today = date.today()
    formatted_todays_date = today.strftime("%a %d %b %Y")

    properties_today = Property.query.filter_by(
        received_date=formatted_todays_date).all()

    properties_today_count = Property.query.filter_by(
        received_date=formatted_todays_date).count()

    return jsonify(
        {
            "count": properties_today_count,
            "properties": list(map(lambda prop: prop.serialize(), properties_today))
        })
