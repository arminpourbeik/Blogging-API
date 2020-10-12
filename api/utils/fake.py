from faker import Faker
from sqlalchemy.exc import IntegrityError

from api.utils.database import db
from api.models.user import User
from api.models.post import Post
from api.models.tag import Tag


def users(count=100):
    fake = Faker()
    i = 0

    while i < count:
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password="p@assw0rd",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            bio=fake.text(),
        )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    from random import randint

    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(), title=fake.text(max_nb_chars=10), author=u)
        db.session.add(p)
    db.session.commit()


def tags():
    tags_ = [
        "Astronomy",
        "Geology",
        "Oceanography",
        "Physics",
        "Earth Science",
        "Chemistry",
        "Botany",
        "Zoology",
        "Biochemistry",
        "Computer Science",
        "Sports",
    ]
    for tag in tags_:
        db.session.add(Tag(name=tag))
        db.session.commit()


def post_tags(max_number_of_tags=5):
    from random import randint

    total_num_of_tags = Tag.query.count()

    for post in Post.query.all():
        num_of_random_tags = randint(0, max_number_of_tags)
        random_selected_tags = Tag.query.offset(
            randint(0, total_num_of_tags - max_number_of_tags)
        ).limit(num_of_random_tags)
        for tag in random_selected_tags:
            post.tags.append(tag)

    db.session.commit()
