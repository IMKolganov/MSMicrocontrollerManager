# app/routes/microcontroller/guid.py

from flask import Blueprint, jsonify
import requests
from app.device_manager import DeviceManager

guid_bp = Blueprint('guid', __name__)

@guid_bp.route('/guid', methods=['GET'])
def get_guid():
    ip = DeviceManager.get_ip()
    try:
        response = requests.get(f'http://{ip}/guid')
        if response.status_code == 200:
            data = response.json()
            return jsonify({'guid': data['guid']}), 200
        else:
            return jsonify({'ErrorMessage': 'Failed to get GUID from ESP32'}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'ErrorMessage': str(e)}), 500
