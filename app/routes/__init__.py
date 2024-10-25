# app/routes/__init__.py

from flask import Blueprint

bp = Blueprint('routes', __name__)

from . import get_ip_esp32, index, healthcheck, device_info

from .microcontroller.guid import guid_bp

bp.register_blueprint(guid_bp, url_prefix='/microcontroller')