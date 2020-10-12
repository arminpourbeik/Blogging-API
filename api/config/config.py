import os

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get("FLASK_ENV")
    PROPAGATE_EXCEPTIONS = True
    JWT_BLACKLIST_ENABLED = True
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    UPLOADED_IMAGES_DEST = os.path.join("static", "images")

    POSTS_PER_PAGE = 10
    USERS_PER_PAGE = 10
    TAGS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    DEBUG = True


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://" + os.path.join(basedir, "test-dev.sqlite")


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_ECHO = False


config = {
    "development": DevConfig,
    "production": ProdConfig,
    "Testing": TestConfig,
    "default": DevConfig,
}
