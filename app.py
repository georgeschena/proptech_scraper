from flask import Flask, escape, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from property_model import Property
import os
from datetime import date

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')


@app.route('/all_properties', methods=['GET'])
def get_all_properties():
    return jsonify(
        {
            "count": Property.query.count(),
            "properties": list(map(lambda prop: prop.serialize(), Property.query.all()))
        })


@app.route('/todays_properties', methods=['GET'])
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


@app.route('/search_properties', methods=['POST'])
def search_properties():
    data = request.get_json()

    council_name = data['council_name']
    description = data['description']

    search_query = Property.query.filter(
        Property.council_name == council_name,
        Property.description.contains(description)).all()

    search_query_count = Property.query.filter(
        Property.council_name == council_name,
        Property.description.contains(description)).count()

    return jsonify(
        {
            "count": search_query_count,
            "properties": list(map(lambda prop: prop.serialize(), search_query))
        })
