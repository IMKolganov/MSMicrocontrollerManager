import json
import time
import pika
import paho.mqtt.client as mqtt
from datetime import datetime

class MessageService:
    def __init__(self, rabbitmq_client, mqtt_client):
        self.rabbitmq_client = rabbitmq_client
        self.mqtt_client = mqtt_client

    def handle_request(self, ch, method, properties, body, app, queue_name):
        """Основной обработчик сообщений."""
        request_data, request_id, method_name, mqtt_topic = self._parse_request(body)
        
        print(f"Received request from queue {queue_name}: RequestId: {request_id}, Method: {method_name}, Data: {request_data}")

        response_queue = self._find_response_queue(app, queue_name)
        if response_queue is None:
            print(f"Error: No response queue found for request queue {queue_name}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        try:
            self._publish_to_mqtt(request_data, mqtt_topic)
            self._send_response(ch, method, properties, app, response_queue, request_id, method_name, '')

        except Exception as e:
            self._send_response(ch, method, properties, app, response_queue, request_id, method_name, str(e), error=True)
            print(f"Failed to send MQTT message. Error: {str(e)}")

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def _parse_request(self, body):
        """Извлечение данных запроса из тела сообщения."""
        request_data = json.loads(body)
        request_id = request_data.get('RequestId')
        method_name = request_data.get('MethodName')
        mqtt_topic = request_data.get('MqttTopic')  # Тема MQTT для публикации
        return request_data, request_id, method_name, mqtt_topic


    def _find_response_queue(self, app, queue_name):
        """Поиск очереди для ответа на основе очереди запроса."""
        for queue_info in app.config['QUEUES'].values():
            if queue_info['request_queue'] == queue_name:
                return queue_info['response_queue']
        return None


    def _publish_to_mqtt(self, request_data, mqtt_topic):
        """Публикация сообщения в MQTT."""
        mqtt_message = json.dumps(request_data)
        self.mqtt_client.publish(mqtt_topic, mqtt_message)
        print(f"Sent MQTT message to {mqtt_topic}: {mqtt_message}")


    def _send_response(self, ch, method, properties, app, response_queue, request_id, method_name, error_message, error=False):
        """Отправка ответа или ошибки в RabbitMQ."""
        response_message = {
            'RequestId': request_id,
            'MethodName': method_name,
            'CreateDate': datetime.utcnow().isoformat(),
            'ErrorMessage': error_message if error else ''
        }

        ch.basic_publish(
            exchange='',
            routing_key=response_queue,
            body=json.dumps(response_message),
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            )
        )
        if error:
            print(f"Response sent with error to {response_queue} RequestId: {request_id}, Error: {error_message}")
        else:
            print(f"Response sent to {response_queue} RequestId: {request_id}, Response: {response_message}")



    def start_listening(self, app):
        time.sleep(3)  # Delay for service readiness
        print("MessageService: Starting to process messages...")

        # Слушаем только очереди, помеченные как "request_queue" в конфигурации
        request_queues = [queue_info['request_queue'] for queue_info in app.config['QUEUES'].values()]

        for queue in request_queues:
            print(f"Listening to request queue: {queue}")
            self.rabbitmq_client.start_queue_listener(
                queue_name=queue,
                on_message_callback=lambda ch, method, properties, body, queue=queue: self.handle_request(ch, method, properties, body, app, queue)
            )

        print("MessageService: Listening for request messages from all request queues...")
