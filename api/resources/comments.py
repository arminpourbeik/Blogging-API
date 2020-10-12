from flask import request, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user
from flask_restful import Resource

from api.models.comment import Comment, CommentSchema
from api.utils.responses import response_with
from api.utils import responses as resp


class CommentListResource(Resource):
    @classmethod
    def get(cls):
        page = request.args.get("page", 1, type=int)
        pagination = Comment.find_all_confirmed().paginate(
            page, per_page=current_app.config["COMMENTS_PER_PAGE"], error_out=False
        )

        get_comments = pagination.items

        prev = None
        if pagination.has_prev:
            prev = url_for("comment-list", page=page - 1)
        _next = None
        if pagination.has_next:
            _next = url_for("comment-list", page=page + 1)

        comments = CommentSchema(many=True, exclude=('confirmed',)).dump(get_comments)
        return response_with(resp.SUCCESS_200, value={'comments': comments}, pagination={'prev': prev, 'next': _next})


class CommentResource(Resource):
    @classmethod
    def get(cls, comment_id: int):
        get_comment = Comment.query.get_or_404(comment_id)
        result = CommentSchema(exclude=('confirmed',)).dump(get_comment)
        return response_with(resp.SUCCESS_200, value={'comment': result})

    @classmethod
    @jwt_required
    def put(cls, comment_id: int):
        user = get_current_user()
        data = request.get_json()
        comment = Comment.query.get_or_404(comment_id)
        if comment.author != user and user.is_admin is not True:
            return response_with(
                resp.FORBIDDEN_403, message="You are not the author of this comment."
            )
        comment_schema = CommentSchema()
        updated_comment = comment_schema.load(data, instance=comment)
        result = comment_schema.dump(updated_comment.save_to_db())
        return response_with(resp.SUCCESS_200, value={"comment": result})

    @classmethod
    @jwt_required
    def delete(cls, comment_id: int):
        user = get_current_user()
        get_comment = Comment.query.get_or_404(comment_id)
        if get_comment.author != user and user.is_admin is not True:
            return response_with(
                resp.FORBIDDEN_403, message="You are not the author of this comment."
            )
        get_comment.delete_from_db()
        return response_with(resp.SUCCESS_204)
