import json
import pika
import time
import paho.mqtt.client as mqtt
from datetime import datetime

class MessageService:
    def __init__(self, rabbitmq_client, mqtt_client):
        self.rabbitmq_client = rabbitmq_client
        self.mqtt_client = mqtt_client
        self.mqtt_response = None

    # 1. Receive the request from RabbitMQ
    def handle_request(self, ch, method, properties, body, app, queue_name):
        try:
            request_data, request_id, method_name, rq_mqtt_topic, rs_mqtt_topic = self._parse_request(body)
            print(f"Received request from RabbitMQ queue {queue_name}: {request_data}")

            self._publish_to_mqtt(request_data, rq_mqtt_topic)

            self._wait_for_mqtt_response(ch, method, properties, app, request_id, method_name, rs_mqtt_topic, queue_name)

        except Exception as e:
            # In case of an error, log the information and reject the message without requeuing it
            print(f"Error processing message: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _parse_request(self, body):
        """Extract request data from the message body."""
        request_data = json.loads(body)

        request_id = request_data.get('RequestId')
        method_name = request_data.get('MethodName')
        rq_mqtt_topic = request_data.get('RqMqttTopic')
        rs_mqtt_topic = request_data.get('RsMqttTopic')

        return request_data, request_id, method_name, rq_mqtt_topic, rs_mqtt_topic

    # 2. Send the request to MQTT
    def _publish_to_mqtt(self, request_data, mqtt_topic):
        """Publish the message to MQTT."""
        mqtt_message = json.dumps(request_data)
        self.mqtt_client.publish(mqtt_topic, mqtt_message)
        print(f"Sent MQTT message to {mqtt_topic}: {mqtt_message}")

    # 3. Wait for the response from MQTT
    def _wait_for_mqtt_response(self, ch, method, properties, app, request_id, method_name, rs_mqtt_topic, queue_name, timeout=3):
        """Wait for the response from MQTT with a timeout and send the response back to RabbitMQ."""
        
        print(f"Subscribing to MQTT topic: {rs_mqtt_topic}")
        
        # Subscribe to the topic to receive the response
        self.mqtt_client.subscribe(rs_mqtt_topic)
        self.mqtt_client.on_message = self.on_mqtt_message

        self.mqtt_client.loop_start()  # Start the loop to receive MQTT messages

        start_time = time.time()
        while self.mqtt_response is None:
            if time.time() - start_time > timeout:
                print(f"Timeout exceeded: No response from MQTT within {timeout} seconds")
                self._handle_mqtt_timeout(ch, method, properties, app, request_id, method_name, rs_mqtt_topic)
                self.mqtt_client.loop_stop()
                return 
            time.sleep(0.1)  # Short pause to reduce CPU load

        # 4. Send the response back to RabbitMQ
        response_queue = self._find_response_queue(app, queue_name)
        if response_queue:
            print(f"Sending response to RabbitMQ queue: {response_queue}")
            self._send_response(ch, method, properties, app, response_queue, request_id, method_name, self.mqtt_response)
        else:
            print(f"Error: No response queue found for request queue {queue_name}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.mqtt_response = None  # Clear for the next message
        self.mqtt_client.loop_stop()

    def on_mqtt_message(self, client, userdata, msg):
        """Handle the message received via MQTT."""
        print(f"Received MQTT response from topic {msg.topic}: {msg.payload}")
        self.mqtt_response = json.loads(msg.payload)

    def _handle_mqtt_timeout(self, ch, method, properties, app, request_id, method_name, queue_name):
        """Handle timeout if no response was received from MQTT."""
        response_queue = self._find_response_queue(app, queue_name)
        if response_queue:
            # Create an error message for RabbitMQ
            error_message = {
                'RequestId': request_id,
                'MethodName': method_name,
                'CreateDate': datetime.utcnow().isoformat(),
                'ErrorMessage': 'Timeout: No response from MQTT'
            }

            ch.basic_publish(
                exchange='',
                routing_key=response_queue,
                body=json.dumps(error_message),
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id
                )
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Timeout response sent to {response_queue} for RequestId: {request_id}")
        else:
            print(f"Error: No response queue found for request queue {queue_name}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _find_response_queue(self, app, queue_name):
        """Find the response queue based on the request queue."""
        for queue_info in app.config['QUEUES'].values():
            if queue_info['request_queue'] == queue_name:
                return queue_info['response_queue']
        return None

    # Send the response back to RabbitMQ
    def _send_response(self, ch, method, properties, app, response_queue, request_id, method_name, mqtt_response):
        """Send the response back to RabbitMQ after receiving data from MQTT."""
        response_message = {
            'RequestId': request_id,
            'MethodName': method_name,
            'CreateDate': datetime.utcnow().isoformat(),
            'ResponseData': mqtt_response
        }

        ch.basic_publish(
            exchange='',
            routing_key=response_queue,
            body=json.dumps(response_message),
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            )
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Response sent to {response_queue} RequestId: {request_id}, Response: {response_message}")


    def start_listening(self, app):
        time.sleep(3)  # Delay for service readiness
        print("MessageService: Starting to process messages...")

        # Listen only to queues marked as "request_queue" in the configuration
        request_queues = [queue_info['request_queue'] for queue_info in app.config['QUEUES'].values()]

        for queue in request_queues:
            print(f"Listening to request queue: {queue}")
            self.rabbitmq_client.start_queue_listener(
                queue_name=queue,
                on_message_callback=lambda ch, method, properties, body, queue=queue: self.handle_request(ch, method, properties, body, app, queue)
            )

        print("MessageService: Listening for request messages from all request queues...")
