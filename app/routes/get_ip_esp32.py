# app/routes/get_ip_esp32.py

from flask import jsonify
from . import bp
from app.utils import receive_ip_from_esp32, fetch_guid_from_esp32
from app.device_manager import DeviceManager
import asyncio

@bp.route('/get-ip-esp32')
def getipesp32():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ip = loop.run_until_complete(receive_ip_from_esp32())
    
    if not ip:
        return jsonify({'error': 'Failed to receive IP from ESP32'}), 500
    
    guid = fetch_guid_from_esp32(ip)
    
    # Update DeviceManager with new IP and GUID
    DeviceManager.set_device_info(ip, guid)
    
    return jsonify({'ip': ip, 'guid': guid}), 200
