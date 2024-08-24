# app/main.py

from flask import Flask
from app.routes import bp as routes_bp
import threading
import os
import sys
from app.clients.rabbit_mq_client import RabbitMQClient
from app.services.soil_moisture_service import SoilMoistureService
from app.services.temperature_humidity_service import TemperatureHumidityService

def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    if env == 'development':
        app.config.from_object('app.config.DevelopmentConfig')
    elif env == 'docker':
        app.config.from_object('app.config.DockerConfig')
    else:
        app.config.from_object('app.config.Config')
    
    app.register_blueprint(routes_bp)
    return app

def handle_signal(signum, frame):
    print('Received signal:', signum)
    # Perform cleanup if needed
    sys.exit(0)


def start_message_processing(app):
    """Starts message processing in a separate thread with application context."""
    import app.services.soil_moisture_service as soil_moisture_service
    rabbitmq_client = RabbitMQClient(host=app.config['RABBITMQ_HOST'], queues=app.config['QUEUES'])

    soil_moisture_service = SoilMoistureService(rabbitmq_client=rabbitmq_client)
    processing_thread = threading.Thread(target=soil_moisture_service.start_listening, args=(app,))
    processing_thread.daemon = True
    processing_thread.start()

    temperature_humidity_service = TemperatureHumidityService(rabbitmq_client=rabbitmq_client)
    processing_thread = threading.Thread(target=temperature_humidity_service.start_listening, args=(app,))
    processing_thread.daemon = True
    processing_thread.start()
    print("Message processing thread started")