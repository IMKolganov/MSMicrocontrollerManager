# app/routes/__init__.py

from flask import Blueprint

bp = Blueprint('routes', __name__)

from . import get_ip_esp32, index, healthcheck, device_info

from .microcontroller.guid import guid_bp
from .microcontroller.soil_moisture import soil_moisture_bp
from .microcontroller.temperature_humidity import temperature_humidity_bp

bp.register_blueprint(guid_bp, url_prefix='/microcontroller')
bp.register_blueprint(soil_moisture_bp, url_prefix='/microcontroller')
bp.register_blueprint(temperature_humidity_bp, url_prefix='/microcontroller')