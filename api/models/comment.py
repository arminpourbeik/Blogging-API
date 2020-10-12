from datetime import datetime
from typing import List

from api.utils.database import db, ma


class Comment(db.Model):
    __tablename__ = "comments"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def save_to_db(self) -> "Comment":
        db.session.add(self)
        db.session.commit()
        return self

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id: int):
        return cls.query.get_or_404(_id)

    @classmethod
    def find_all(cls) -> List["Comment"]:
        return cls.query.all()

    @classmethod
    def find_all_confirmed(cls) -> List["Comment"]:
        return cls.query.filter_by(confirmed=True)


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True
        load_only = ('user_id', 'post_id')
        dump_only = ('confirmed',)

    id = ma.auto_field()
    user_id = ma.auto_field()
    post_id = ma.auto_field()
    body = ma.auto_field()
    timestamp = ma.auto_field()
