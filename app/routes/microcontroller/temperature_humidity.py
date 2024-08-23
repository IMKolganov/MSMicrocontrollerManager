# app/routes/microcontroller/temperature_humidity.py

from flask import Blueprint, jsonify
import requests
from app.device_manager import DeviceManager

temperature_humidity_bp = Blueprint('temperature_humidity', __name__)

@temperature_humidity_bp.route('/temperature-humidity', methods=['GET'])
def get_temperature_humidity():
    ip = DeviceManager.get_ip()
    try:
        response = requests.get(f'http://{ip}/temperature-humidity')
        if response.status_code == 200:
            data = response.json()
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Failed to get temperature and humidity from ESP32'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
