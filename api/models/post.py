from datetime import datetime
from typing import List

from marshmallow import pre_dump, fields

from api.models.tag import Tag, TagSchema
from api.models.user import UserSchema
from api.models.comment import CommentSchema, Comment
from api.utils.database import db, ma

post_tag = db.Table(
    "post_tag",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Post(db.Model):
    __tablename__ = "posts"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text)
    title = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Relationships
    tags = db.relationship(Tag, secondary=post_tag, backref=db.backref("posts_"))
    author = db.relationship("User", backref="posts")
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def save_to_db(self) -> "Post":
        db.session.add(self)
        db.session.commit()
        return self

    def add_to_session(self):
        db.session.add(self)

    def db_commit(self):
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @property
    def comments_count(self):
        return self.comments.filter_by(confirmed=True).count()

    @classmethod
    def find_all_confirmed(cls) -> List["Post"]:
        return cls.query.filter_by(confirmed=True).order_by(cls.timestamp.desc())


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True

    title = ma.auto_field()
    id = ma.auto_field(dump_only=True)
    timestamp = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(load_only=True)
    body = ma.auto_field()
    author = ma.Nested(UserSchema, only=["id", "username", "email"], dump_only=True)
    tags = ma.Pluck(TagSchema, "name", many=True)

    comments = ma.Nested('CommentSchema', many=True, dump_only=True)
    comments_count = fields.Integer(dump_only=True)

    @pre_dump
    def _pre_dump(self, post, **kwargs):
        post.comments = post.comments.filter_by(confirmed=True)
        return post
