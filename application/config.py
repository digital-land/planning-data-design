# -*- coding: utf-8 -*-
import os

from application.utils import to_boolean

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    DEBUG = False
    AUTHENTICATION_ON = to_boolean(os.getenv("AUTHENTICATION_ON", True))
    GOOGLE_PRIVATE_KEY_ID = os.getenv("GOOGLE_PRIVATE_KEY_ID")
    GOOGLE_PRIVATE_KEY = os.getenv("GOOGLE_PRIVATE_KEY")
    GOOGLE_CLIENT_EMAIL = os.getenv("GOOGLE_CLIENT_EMAIL")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    SAFE_URLS = set(os.getenv("SAFE_URLS", "").split(","))
    PLATFORM_URL = os.getenv("PLATFORM_URL", "https://www.planning.data.gov.uk")
    DATASET_EDITOR_URL = os.getenv(
        "DATASET_EDITOR_URL", "http://dataset-editor.planning.data.gov.uk"
    )
    LOAD_QUESTIONS = to_boolean(os.getenv("LOAD_QUESTIONS", False))


class DevelopmentConfig(Config):
    DEBUG = False
    ENV = "development"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestConfig(Config):
    ENV = "test"
    DEBUG = True
    TESTING = True
    SERVER_NAME = "localhost"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:postgres@localhost/test_considerations"
    )
    AUTHENTICATION_ON = False
