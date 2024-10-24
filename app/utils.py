# app/utils.py

import asyncio
import socket
# import requests

async def receive_ip_from_esp32(port=6000):
    # loop = asyncio.get_event_loop()
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind(('0.0.0.0', port))
    
    # data, _ = await loop.run_in_executor(None, sock.recvfrom, 1024)
    
    # sock.close()
    
    return '192.168.10.35'#data.decode('utf-8')

def fetch_guid_from_esp32(ip):
    try:
        response = requests.get(f'http://{ip}/guid')
        response.raise_for_status()
        return response.json().get('guid', 'GUID not found')
    except requests.RequestException as e:
        return str(e)
