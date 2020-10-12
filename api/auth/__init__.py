from flask_jwt_extended import JWTManager

from api.models.user import User


jwt = JWTManager()


@jwt.user_loader_callback_loader
def user_loader(identity):
    return User.find_by_username(username=identity)


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = User.find_by_username(username=identity)

    if user and user.is_admin:
        return {"is_admin": True}
    else:
        return {"is_admin": False}
