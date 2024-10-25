# app/main.py

from flask import Flask
from app.routes import bp as routes_bp
import threading
import os
import sys
from app.clients.rabbit_mq_client import RabbitMQClient
from app.services.message_service import MessageService
import paho.mqtt.client as mqtt

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

    # Инициализация RabbitMQ клиента
    rabbitmq_client = RabbitMQClient(host=app.config['RABBITMQ_HOST'], queues=app.config['QUEUES'])

    # Инициализация MQTT клиента
    mqtt_client = mqtt.Client()
    mqtt_client.connect(app.config['RABBITMQ_HOST'], 1883, 60)  # Укажите адрес и порт вашего брокера

    # Создаем объект MessageService с двумя клиентами
    message_service = MessageService(rabbitmq_client=rabbitmq_client, mqtt_client=mqtt_client)

    # Запускаем обработку сообщений в отдельном потоке
    processing_thread = threading.Thread(target=message_service.start_listening, args=(app,))
    processing_thread.daemon = True
    processing_thread.start()

    print("Message processing thread started")