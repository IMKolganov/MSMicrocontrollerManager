# app/config.py

import os

class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

    QUEUES = {
        "get_soil_moisture": {
            "request_queue": "msgetsoilmoisture.to.msmicrocontrollermanager.request",
            "response_queue": "msmicrocontrollermanager.to.msgetsoilmoisture.response"
        },
        "get_temperature_and_humidity": {
            "request_queue": "msgettemperatureandhumidify.to.msmicrocontrollermanager.request",
            "response_queue": "msmicrocontrollermanager.to.msgettemperatureandhumidify.response"
        },
        "pump_control": {
            "request_queue": "mspumpcontrol.to.msmicrocontrollermanager.request",
            "response_queue": "msmicrocontrollermanager.to.mspumpcontrol.response"
        }
    }


class DevelopmentConfig(Config):
    DEBUG = True
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    MICROCONTROLLER_MANAGER_URL = os.getenv('MICROCONTROLLER_MANAGER_URL', 'http://localhost:4000')


class DockerConfig(Config):
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    MICROCONTROLLER_MANAGER_URL = os.getenv('MICROCONTROLLER_MANAGER_URL', 'http://microcontroller_manager:4000')