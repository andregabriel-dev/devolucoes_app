import os

class Config:
    SECRET_KEY = 'sua_chave_super_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False