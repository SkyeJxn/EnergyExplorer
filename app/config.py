import socket
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
    
CONFIG = {
    "dev" : {
        "debug": True,
        "host": "localhost",
        "port": 8080,
    },
    "pre-prod" : {
        "host": get_local_ip(),
        "dev_ui_tools": False,
        "port": 8080,
    },
    "prod" : {
        "host": "0.0.0.0",
        "port": 8080,
    }
}