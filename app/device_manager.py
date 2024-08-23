# app/device_manager.py

import asyncio
from app.utils import receive_ip_from_esp32, fetch_guid_from_esp32

class DeviceManager:
    _ip = None
    _guid = None

    @classmethod
    def set_device_info(cls, ip, guid):
        cls._ip = ip
        cls._guid = guid

    @classmethod
    def _ensure_device_info(cls):

        if cls._ip is None or cls._guid is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ip = loop.run_until_complete(receive_ip_from_esp32())

            if not ip:
                raise RuntimeError('Failed to receive IP from ESP32')

            guid = fetch_guid_from_esp32(ip)
            
            if not guid:
                raise RuntimeError('Failed to fetch GUID from ESP32')

            cls.set_device_info(ip, guid)

    @classmethod
    def get_ip(cls):
        cls._ensure_device_info()
        return cls._ip

    @classmethod
    def get_guid(cls):
        cls._ensure_device_info()
        return cls._guid

    @classmethod
    def clear_device_info(cls):
        cls._ip = None
        cls._guid = None
