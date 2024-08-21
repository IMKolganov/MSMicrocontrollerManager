# app/routes/__init__.py

from flask import Blueprint

bp = Blueprint('routes', __name__)

from . import get_ip_esp32, index, healthcheck, random_bluetooth, random_usb, random_wifi, device_info