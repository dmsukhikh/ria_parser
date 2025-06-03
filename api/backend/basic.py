# this file is for basic definitions of flask app
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL

app = flask.Flask(__name__)

# configuration for entering the database
app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
    database='ria',
    host='localhost',
    username='server',
    password='server52BOB',
    drivername='postgresql',
    port=8085
).render_as_string(hide_password=False)

print(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

