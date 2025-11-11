from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# Example: using SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# --- JWT config ---
app.config["JWT_SECRET_KEY"] = "change-me"  # put in ENV in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#model
import model

#route
import route

#Function
import Function

if __name__ == '__main__':
    app.run()
