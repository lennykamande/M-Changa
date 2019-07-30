import os

class Config(object):
    debug = False
    TESTING = False
    db_user = environ.get('DATABASE_USER')
    db_password = environ.get('DATABASE_PASSWORD')
    db_host = environ.get('DATABASE_HOST')
    db_port = environ.get('DATABASE_PORT')
    db_name = environ.get('DATABASE_NAME')

class TestingConfig(Config):
    """ Testing configurations """

    DEBUG = True
    TESTING = True
    db_host = "secure.changa.db.prod"
    db_name = "root"
    db_password = "!@pplasddHXKL)_"
    db_name = "sec_changa"
    db_port = 3306


class ProductionConfig(Config):
    """ Production configurations """

    DEBUG = False
    TESTING = False
    db_host = "secure.changa.db.prod"
    db_name = "root"
    db_password = "!@pplasddHXKL)_"
    db_name = "sec_changa"
    db_port = 3306

app_config = {
    "testing": TestingConfig,
    "production": ProductionConfig
}