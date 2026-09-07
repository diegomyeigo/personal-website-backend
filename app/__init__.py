from flask import Flask
from flask_cors import CORS
import os
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)

    ORIGIN = os.environ.get("CORS_ORIGIN")
    CORS(app, origins=[ORIGIN])

    app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL")

    app.config["MAIL_SERVER"] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

    mail.init_app(app)

    from .routes import routes
    app.register_blueprint(routes)

    return app
