# app/device_manager.py

class DeviceManager:
    _ip = None
    _guid = None

    @classmethod
    def set_device_info(cls, ip, guid):
        cls._ip = ip
        cls._guid = guid

    @classmethod
    def get_ip(cls):
        return cls._ip

    @classmethod
    def get_guid(cls):
        return cls._guid

    @classmethod
    def clear_device_info(cls):
        cls._ip = None
        cls._guid = None
