from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://Dadmin:Tigrou007@localhost/mydb'
# heimdall:e^t~^ChzAY^I5d-CV?l6
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

