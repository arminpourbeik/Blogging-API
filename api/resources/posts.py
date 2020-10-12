from flask import current_app, url_for
from flask_restful import Resource, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_current_user

from api.models.post import Post, PostSchema
from api.models.tag import TagSchema, Tag
from api.models.user import User
from api.models.comment import Comment, CommentSchema
from api.utils import responses as resp
from api.utils.responses import response_with
from api.utils.decorators import admin_required


class PostListResource(Resource):
    @classmethod
    def get(cls):
        page = request.args.get("page", 1, type=int)
        pagination = Post.query.paginate(
            page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
        get_posts = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for("post-list", page=page - 1)
        _next = None
        if pagination.has_next:
            _next = url_for("post-list", page=page + 1)

        posts_schema = PostSchema(many=True, exclude=["user_id", "body", "comments"])
        posts = posts_schema.dump(get_posts)

        return response_with(
            resp.SUCCESS_200,
            value={"posts": posts},
            pagination={"prev": prev, "next": _next, "count": pagination.total},
        )

    @classmethod
    @jwt_required
    def post(cls):
        author = get_current_user()
        data = request.get_json()
        data["user_id"] = author.id
        incoming_tags = None

        if data["tags"] is not None:
            incoming_tags = [{"name": tag} for tag in data["tags"]]

        del data["tags"]

        post_schema = PostSchema(exclude=["tags"], partial=True)
        post = post_schema.load(data)

        post.add_to_session()

        for _tag in incoming_tags:
            tag = TagSchema().load(_tag)
            tag_in_db = Tag.query.filter_by(name=tag.name).first()
            if tag_in_db:
                post.tags.append(tag_in_db)
            else:
                post.tags.append(tag)

        post.db_commit()
        result = PostSchema().dump(post)

        return response_with(resp.SUCCESS_201, value={"post": result})


class PostResource(Resource):
    @classmethod
    def get(cls, _id):
        get_post = Post.query.get_or_404(_id)
        post = PostSchema().dump(get_post)
        return response_with(resp.SUCCESS_200, value={"post": post})

    @classmethod
    def patch(cls, _id):
        data = request.get_json()
        post = Post.query.get_or_404(_id)
        post_schema = PostSchema()
        updated_post = post_schema.load(data, instance=post, partial=True)
        result = post_schema.dump(updated_post.save_to_db())
        return response_with(resp.SUCCESS_200, value={"post": result})

    @classmethod
    @jwt_required
    def put(cls, _id):
        user = get_current_user()
        data = request.get_json()
        post = Post.query.get_or_404(_id)
        if post.author != user and user.is_admin is not True:
            if post.author != user and user.is_admin is not True:
                return response_with(
                    resp.FORBIDDEN_403, message="You are not the author of this post."
                )
        post_schema = PostSchema()
        updated_post = post_schema.load(data, instance=post)
        result = post_schema.dump(updated_post.save_to_db())
        return response_with(resp.SUCCESS_200, value={"post": result})

    @classmethod
    @jwt_required
    def delete(cls, _id):
        post = Post.query.get_or_404(_id)
        user = get_current_user()
        if post.author != user and user.is_admin is not True:
            return response_with(
                resp.FORBIDDEN_403, message="You are not the author of this post."
            )
        post.delete_from_db()
        return response_with(resp.SUCCESS_204)


class UserPostResource(Resource):
    @classmethod
    def get(cls, username: str):
        page = request.args.get("page", 1, type=int)
        user = User.find_by_username(username)
        if not user:
            return response_with(
                resp.SERVER_ERROR_404,
                message=f"user with username: {username} not found.",
            )
        pagination = (
            Post.query.filter_by(author=user)
            .order_by(Post.timestamp.desc())
            .paginate(
                page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
            )
        )
        get_posts = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for("post-list", page=page - 1)
        _next = None
        if pagination.has_next:
            _next = url_for("post-list", page=page + 1)

        posts_schema = PostSchema(many=True, exclude=["user_id", "body"])
        posts = posts_schema.dump(get_posts)

        return response_with(
            resp.SUCCESS_200,
            value={"posts": posts},
            pagination={"prev": prev, "next": _next, "count": pagination.total},
        )


class PostCommentResource(Resource):
    @classmethod
    @jwt_required
    def post(cls, post_id: int):
        post = Post.query.get_or_404(post_id)
        user = get_current_user()
        data = request.get_json()
        data['user_id'] = user.id
        data['post_id'] = post.id
        comment = CommentSchema().load(data)
        result = CommentSchema(exclude=('confirmed',)).dump(comment.save_to_db())

        return response_with(resp.SUCCESS_201, value=result)


