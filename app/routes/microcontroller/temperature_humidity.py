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
            try:
                error_message = response.json().get('error', 'Unknown error')
            except ValueError:
                error_message = response.text
            return jsonify({'ErrorMessage': error_message}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'ErrorMessage': str(e)}), 500