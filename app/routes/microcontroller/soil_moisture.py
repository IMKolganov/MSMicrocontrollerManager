# app/routes/microcontroller/soil_moisture.py

from flask import Blueprint, jsonify
import requests
from app.device_manager import DeviceManager

soil_moisture_bp = Blueprint('soil_moisture', __name__)

@soil_moisture_bp.route('/soil-moisture', methods=['GET'])
def get_soil_moisture():
    ip = DeviceManager.get_ip()
    try:
        response = requests.get(f'http://{ip}/soil-moisture')
        if response.status_code == 200:
            data = response.json()
            return jsonify(data), 200
        else:
            return jsonify({'ErrorMessage': 'Failed to get soil moisture from ESP32'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'ErrorMessage': str(e)}), 500
