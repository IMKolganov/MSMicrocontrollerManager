# app/routes/device_info.py

from flask import jsonify
from . import bp
from app.device_manager import DeviceManager

@bp.route('/device-info')
def device_info():
    ip = DeviceManager.get_ip()
    guid = DeviceManager.get_guid()

    if not ip or not guid:
        return jsonify({'ErrorMessage': 'Device information is not available'}), 404
    
    return jsonify({'ip': ip, 'guid': guid}), 200
