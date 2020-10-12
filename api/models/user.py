import os
from datetime import datetime
from typing import List
from requests import Response
from flask import request, url_for

from api.models.comment import Comment
from api.models.confirmation import Confirmation
from api.utils.email import Mailgun
from marshmallow.fields import Nested
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import pre_dump
from marshmallow.validate import Email

from api.utils.database import db, ma


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    avatar = db.Column(db.String(164))
    password_hash = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)

    # Relationship
    confirmation = db.relationship(
        "Confirmation", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        Comment, backref="author", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.email == os.environ.get("ADMIN_EMAIL"):
            self.is_admin = True
        else:
            self.is_admin = False

    @property
    def most_recent_confirmation(self) -> "Confirmation":
        return self.confirmation.order_by(db.desc(Confirmation.expire_at)).first()

    def save_to_db(self) -> "User":
        db.session.add(self)
        db.session.commit()
        return self

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls) -> List["User"]:
        return cls.query.all()

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_username(cls, username) -> "User":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email) -> "User":
        return cls.query.filter_by(email=email).first()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[0:-1] + url_for(
            "confirmationresource", confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Registration confirmation"
        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"

        return Mailgun.send_email(
            to=[self.email], subject=subject, text=text, html=html
        )


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        fields = (
            "id",
            "first_name",
            "password",
            "last_name",
            "email",
            "username",
            "avatar",
            "bio",
            "timestamp",
            "confirmation",
            "posts",
        )
        dump_only = ("id", "confirmation", "timestamp")

    password = ma.String(load_only=True)
    email = ma.Email(required=True, validate=Email())

    posts = Nested("PostSchema", many=True, only=("title", "id"), dump_only=True)

    @pre_dump
    def _pre_dump(self, user, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
