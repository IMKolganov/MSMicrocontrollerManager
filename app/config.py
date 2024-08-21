# app/config.py

import os

class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
 
class DevelopmentConfig(Config):
    DEBUG = True
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class DockerConfig(Config):
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
