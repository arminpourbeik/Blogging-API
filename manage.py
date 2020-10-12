from flask import Flask
from flask_restful import Api
from flask_uploads import patch_request_class, configure_uploads

from api.config.config import config
from api.utils.database import db, ma
from api.utils.image_helper import IMAGE_SET
from api.auth import jwt

from api.routes import initialize_routes


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    patch_request_class(app, 10 * 1024 * 1024)  # 10MB max image size upload
    configure_uploads(app, IMAGE_SET)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    api = Api(app)

    initialize_routes(api)

    return app
