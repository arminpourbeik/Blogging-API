from flask import request, current_app, url_for
from flask_restful import Resource

from api.models.tag import Tag, TagSchema
from api.utils import responses as resp
from api.utils.responses import response_with

tags_schema = TagSchema(many=True)
tag_schema = TagSchema()


class TagListResource(Resource):
    @classmethod
    def get(cls):
        page = request.args.get("page", 1, type=int)
        pagination = Tag.query.paginate(
            page, per_page=current_app.config["TAGS_PER_PAGE"], error_out=False
        )
        get_tags = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for("tag-list", page=page - 1)
        _next = None
        if pagination.has_next:
            _next = url_for("tag-list", page=page + 1)

        tags = tags_schema.dump(get_tags)
        return response_with(
            resp.SUCCESS_200,
            value={"tags": tags},
            pagination={"prev": prev, "next": _next, "count": pagination.total},
        )

    @classmethod
    def post(cls):
        data = request.get_json()
        tag = TagSchema().load(data)
        result = TagSchema().dump(tag.save_to_db())
        return response_with(resp.SUCCESS_201, value={"tag": result})


class TagResource(Resource):
    @classmethod
    def get(cls, _id):
        get_tag = Tag.query.get_or_404(_id)
        tag = tag_schema.dump(get_tag)
        return response_with(resp.SUCCESS_200, value={"tag": tag})
