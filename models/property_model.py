from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)


class Properties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=True)
    council_name = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    refernce_number = db.Column(db.String(255),  nullable=True)
    received_date = db.Column(db.String(255),  nullable=True)
    validated_date = db.Column(db.String(255),  nullable=True)
    status = db.Column(db.String(255),  nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "council_name": self.council_name,
            "address": self.address,
            "description": self.description,
            "refernce_number": self.refernce_number,
            "received_date": self.received_date,
            "validated_date": self.validated_date,
            "status": self.status
        }
