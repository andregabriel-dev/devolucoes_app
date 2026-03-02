import os

class Config:
    # Ele tenta pegar a chave do Render, se não tiver, usa 'chave-muito-secreta'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-muito-secreta-de-teste'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False