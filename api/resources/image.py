import os
import traceback

from flask import request, send_file
from flask_jwt_extended import jwt_required, get_current_user, get_jwt_identity
from flask_restful import Resource
from flask_uploads import UploadNotAllowed

from api.schemas.image import ImageSchema
from api.utils import image_helper
from api.utils import responses as resp
from api.utils.responses import response_with

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        Used to upload an image file.
        It uses JWT to retrieve user information and then saves the image to the user's folder.
        If there is a filename conflict, it appends a number at the end.
        """
        data = image_schema.load(request.files)  # {"image": FileStorage}
        user = get_current_user()
        folder = f"{user.username}"  # static/images/<username>

        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return response_with(
                resp.SUCCESS_201, message="Image {} uploaded.".format(basename)
            )
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return response_with(
                resp.BAD_REQUESTS_400,
                message="file with {} format not allowed.".format(extension),
            )


class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        """Returns the requested image if it exists. Look up inside the logged in user's folder."""
        user = get_current_user()
        folder = f"{user.username}"
        if not image_helper.is_filename_safe(filename):
            return response_with(
                resp.BAD_REQUESTS_400, message="illegal_file_name {}".format(filename)
            )

        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return response_with(resp.SERVER_ERROR_404, message="Image not found.")

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user = get_current_user()
        folder = f"{user.username}"
        if not image_helper.is_filename_safe(filename):
            return response_with(
                resp.BAD_REQUESTS_400, message="illegal_file_name {}".format(filename)
            )

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return response_with(resp.SUCCESS_204, message="image deleted")
        except FileNotFoundError:
            return response_with(resp.SERVER_ERROR_404, message="Image not found.")
        except:
            traceback.print_exc()
            return response_with(
                resp.SERVER_ERROR_500, message="Image deletion failed."
            )


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        """
        Used to upload user avatars. All avatars are named after the user's ID.
        Something like this user_{id}.{ext}
        Uploading a new avatar overwrites the existing one.
        """
        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "avatars"
        avatar_path = image_helper.find_image_by_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return response_with(resp.SERVER_ERROR_500, message="deletion failed.")

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )
            basename = image_helper.get_basename(avatar_path)
            return response_with(
                resp.SUCCESS_200, message="avatar {} uploaded.".format(basename)
            )
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return response_with(
                resp.BAD_REQUESTS_400,
                message="file with {} format not allowed.".format(extension),
            )


class Avatar(Resource):
    @classmethod
    def get(cls, username: str):
        folder = "avatars"
        filename = f"user_{username}"
        avatar = image_helper.find_image_by_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        else:
            return response_with(resp.SERVER_ERROR_404, message="avatar not found.")
