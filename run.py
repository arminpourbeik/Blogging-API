import os
from flask_migrate import Migrate
from marshmallow import ValidationError

from manage import create_app
from api.utils.database import db
from api.utils.responses import response_with
from api.utils import responses as resp
from api.auth.blacklist import BLACKLIST
from api.auth import jwt

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app=app, db=db)

from api.models.comment import Comment
from api.models.user import User
from api.models.post import Post
from api.models.tag import Tag
from api.models.confirmation import Confirmation


@app.shell_context_processor
def shell_context():
    return dict(db=db, Comment=Comment,  User=User, Post=Post, Tag=Tag,  Confirmation=Confirmation)


@app.errorhandler(ValidationError)
def marshmallow_validation_error_handler(err):
    return response_with(resp.INVALID_INPUT_422, message=err.messages)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


@app.errorhandler(400)
def bad_request(e):
    # TODO: learn python logging module
    # logging.error(e)
    return response_with(resp.BAD_REQUESTS_400)


@app.errorhandler(500)
def bad_request(e):
    return response_with(resp.SERVER_ERROR_500)


@app.errorhandler(404)
def not_found(e):
    return response_with(resp.SERVER_ERROR_404)
