from flask import Flask
from app.modules.main.route import main_bp
from app.db.db import db


def initialize_route(app: Flask):
    with app.app_context():
        app.register_blueprint(main_bp)


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()
