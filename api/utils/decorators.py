from functools import wraps
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request

from api.utils.responses import response_with
from api.utils import responses as resp


def admin_required(fn):
    wraps(fn)

    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims.get("is_admin", None) is True:
            return fn(*args, **kwargs)
        else:
            return response_with(
                resp.FORBIDDEN_403, message="Admin permission required"
            )

    return wrapper


# def is_author(post_id: int):
#     def inner(fn):
#         wraps(fn)
#
#         def wrapper(*args, **kwargs):
#             verify_jwt_in_request()
#             user = get_current_user()
#             post = Post.query.get_or_404(post_id)
#             if post.author.username == user.username or user.is_admin:
#                 fn(*args, **kwargs)
#             else:
#                 return response_with(resp.FORBIDDEN_403, message='You are not the author of this post')
#
#         return wrapper
#
#     return inner
