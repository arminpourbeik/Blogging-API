from typing import List
from marshmallow import fields, validate

from api.utils.database import db, ma


class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, index=True, unique=True)

    def create(self) -> "Tag":
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_all(cls) -> List["Tag"]:
        return cls.query.all()


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True

    id = ma.Integer(dump_only=True)
    name = ma.String(required=True, validate=validate.Length(max=64))
