from api.resources.confirmation import ConfirmationByUser, ConfirmationResource
from api.resources.image import ImageUpload, Image, AvatarUpload, Avatar
from api.resources.posts import PostListResource, PostResource, UserPostResource, PostCommentResource
from api.resources.tags import TagListResource, TagResource
from api.resources.comments import CommentListResource, CommentResource
from api.resources.users import (
    UserListResource,
    UserResource,
    UserRegister,
    UserLogin,
    UserLogout,
)


def initialize_routes(api):
    api.add_resource(UserRegister, "/register")
    api.add_resource(UserLogin, "/login")
    api.add_resource(UserLogout, "/logout")
    api.add_resource(UserListResource, "/users", endpoint="user-list")
    api.add_resource(UserResource, "/users/<int:_id>")
    api.add_resource(
        UserPostResource, "/<string:username>/posts", endpoint="user-posts-list"
    )
    api.add_resource(ImageUpload, "/upload/image")
    api.add_resource(Image, "/image/<string:filename>")
    api.add_resource(AvatarUpload, "/upload/avatar")
    api.add_resource(Avatar, "/avatar/<string:username>")
    api.add_resource(PostListResource, "/posts", endpoint="post-list")
    api.add_resource(PostCommentResource, '/posts/<int:post_id>/comment', endpoint='post-comment')
    api.add_resource(PostResource, "/posts/<int:_id>")
    api.add_resource(TagListResource, "/tags", endpoint="tag-list")
    api.add_resource(TagResource, "/tags/<int:_id>")
    api.add_resource(ConfirmationResource, "/user_confirm/<string:confirmation_id>")
    api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
    api.add_resource(CommentListResource, '/comments', endpoint='comment-list')
    api.add_resource(CommentResource, '/comments/<int:comment_id>', endpoint='comment')

