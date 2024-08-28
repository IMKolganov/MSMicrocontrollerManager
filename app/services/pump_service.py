import json
import time
import pika
import requests
from datetime import datetime

from app.device_manager import DeviceManager

class PumpService:
    def __init__(self, rabbitmq_client):
        self.rabbitmq_client = rabbitmq_client

    def handle_request(self, ch, method, properties, body, app):
        request_data = json.loads(body)
        request_id = request_data.get('RequestId')
        method_name = request_data.get('MethodName')
        correlation_id = properties.correlation_id
        print(f"Request from {app.config['MSPUMPCONTROL_TO_MSMICROCONTROLLERMANAGER_REQUEST_QUEUE']} "
            f"RequestId: {request_id}, Request: {request_data}")

        if method_name == 'start-pump':
            ip = DeviceManager.get_ip()
            
            try:
                # Perform HTTP GET request with a timeout of 5 seconds
                response = requests.get(f'http://{ip}/start-pump', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    response_message = {
                        'RequestId': request_id,
                        'MethodName': method_name,
                        'Status': data.get('status', ''),
                        'CreateDate': datetime.utcnow().isoformat()
                    }
                    ch.basic_publish(
                        exchange='',
                        routing_key=app.config['MSMICROCONTROLLERMANAGER_TO_MSPUMPCONTROL_RESPONSE_QUEUE'],
                        body=json.dumps(response_message),
                        properties=pika.BasicProperties(
                            correlation_id=correlation_id
                        )
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"Response sent to {app.config['MSMICROCONTROLLERMANAGER_TO_MSPUMPCONTROL_RESPONSE_QUEUE']} "
                        f"RequestId: {request_id}, Response: {response_message}")


                else:
                    try:
                        error_message_esp = response.json().get('error', 'Unknown error')
                    except ValueError:
                        error_message_esp = response.text
                    error_message = {'ErrorMessage': f'Failed to start pump from ESP32. Response: {error_message_esp}'}
                    ch.basic_publish(
                        exchange='',
                        routing_key=app.config['MSMICROCONTROLLERMANAGER_TO_MSPUMPCONTROL_RESPONSE_QUEUE'],
                        body=json.dumps(error_message),
                        properties=pika.BasicProperties(
                            correlation_id=correlation_id
                        )
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"Failed to start pump from ESP32. Error: {error_message}" f"RequestId: {request_id}")

            except requests.exceptions.Timeout:
                timeout_error_message = {
                    'ErrorMessage': 'Request to ESP32 timed out.',
                    'correlation_id': correlation_id
                }
                ch.basic_publish(
                    exchange='',
                    routing_key=app.config['MSMICROCONTROLLERMANAGER_TO_MSPUMPCONTROL_RESPONSE_QUEUE'],
                    body=json.dumps(timeout_error_message),
                    properties=pika.BasicProperties(
                        correlation_id=correlation_id
                    )
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(f"Timeout expired. Error: {timeout_error_message} " f"RequestId: {request_id}")

            except requests.exceptions.RequestException as e:
                request_error_message = {
                    'ErrorMessage': f'Error while receiving data from ESP32: {str(e)}' f'RequestId: {request_id}',
                }
                ch.basic_publish(
                    exchange='',
                    routing_key=app.config['MSMICROCONTROLLERMANAGER_TO_MSPUMPCONTROL_RESPONSE_QUEUE'],
                    body=json.dumps(request_error_message),
                    properties=pika.BasicProperties(
                        correlation_id=correlation_id
                    )
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print(f"PumpService: Message handling failed due to error: {e}")

        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            print(f"PumpService: Unhandled method '{method_name}'. Message nack'ed.")

    def start_listening(self, app):
        time.sleep(3)  # Delay for service readiness
        print("PumpService: Starting to process messages...")
        self.rabbitmq_client.start_queue_listener(
            queue_name=app.config['MSPUMPCONTROL_TO_MSMICROCONTROLLERMANAGER_REQUEST_QUEUE'],
            on_message_callback=lambda ch, method, properties, body: self.handle_request(ch, method, properties, body, app)
        )
        print("PumpService: Listening for messages...")
