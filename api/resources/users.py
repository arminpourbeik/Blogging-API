import traceback

from flask import request, current_app, url_for
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_raw_jwt,
)
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError


from api.models.user import User, UserSchema
from api.models.confirmation import Confirmation
from api.utils.responses import response_with
from api.utils import responses as resp
from api.auth.blacklist import BLACKLIST
from api.utils.email import MailgunException

USER_NOT_FOUND = "User not found."
USER_LOGGED_OUT = "User {} successfully logged out."
USER_ALREADY_EXISTS = "User with this username or email is already exists."
FAILED_TO_CREATE = "Internal server error. Failed to create user."
SUCCESS_REGISTER_MESSAGE = "Account created successfully, an email with an activation link has been sent to yor email address."


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        user = UserSchema().load(data)
        if User.find_by_email(user.email):
            return response_with(
                resp.BAD_REQUESTS_400,
                message=USER_ALREADY_EXISTS,
            )
        try:
            user.save_to_db()
            confirmation = Confirmation(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return response_with(resp.SUCCESS_201, message=SUCCESS_REGISTER_MESSAGE)
        except MailgunException as e:
            user.delete_from_db()
            return response_with(resp.SERVER_ERROR_500, message=str(e))
        except IntegrityError as err:
            return response_with(resp.BAD_REQUESTS_400, message=USER_ALREADY_EXISTS)
        except:
            traceback.print_exc()
            user.delete_from_db()
            return response_with(resp.SERVER_ERROR_500, message=FAILED_TO_CREATE)


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = request.get_json()
        current_user = None
        if data.get("email"):
            current_user = User.find_by_email(data["email"])
        elif data.get("username"):
            current_user = User.find_by_username(data["username"])
        if not current_user:
            return response_with(resp.SERVER_ERROR_404, message=USER_NOT_FOUND)
        if current_user.check_password(data["password"]):
            confirmation = current_user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=current_user.username)
                return response_with(
                    resp.SUCCESS_200,
                    value={"access_token": access_token},
                    message=f"logged in as {current_user.username}",
                )
        else:
            return response_with(resp.FORBIDDEN_403)


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is `JWT ID`, a unique identifier for a JWT.
        BLACKLIST.add(jti)
        username = get_jwt_identity()
        return response_with(resp.SUCCESS_200, message=USER_LOGGED_OUT.format(username))


class UserListResource(Resource):
    @classmethod
    @jwt_required
    def get(cls):

        page = request.args.get("page", 1, type=int)
        pagination = User.query.paginate(
            page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False
        )
        get_users = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for("user-list", page=page - 1)
        _next = None
        if pagination.has_next:
            _next = url_for("user-list", page=page + 1)

        users_schema = UserSchema(many=True, exclude=("posts",))
        users = users_schema.dump(get_users)

        return response_with(
            resp.SUCCESS_200,
            value={"users": users},
            pagination={"prev": prev, "next": _next, "count": pagination.total},
        )


class UserResource(Resource):
    @classmethod
    def get(cls, _id):
        get_user = User.query.get_or_404(_id)
        user = UserSchema().dump(get_user)
        return response_with(resp.SUCCESS_200, value={"user": user})

    @classmethod
    def put(cls, _id):
        user = User.query.get_or_404(_id)
        updatable_fields = ("first_name", "last_name", "username", "avatar", "bio")
        data = request.get_json()

        user_schema = UserSchema(only=updatable_fields)
        updated_user_info = user_schema.load(data, instance=user, partial=True)
        result = UserSchema(only=updatable_fields).dump(updated_user_info.save_to_db())
        return response_with(resp.SUCCESS_200, value={"user": result})

    @classmethod
    def delete(cls, _id):
        user = User.query.get_or_404(_id)
        user.delete_from_db()
        return response_with(resp.SUCCESS_204)
