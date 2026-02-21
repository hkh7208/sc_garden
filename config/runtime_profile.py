import os
import socket
from typing import Set


def _local_ipv4_addresses() -> Set[str]:
    addresses: Set[str] = {'127.0.0.1'}

    try:
        _, _, ip_list = socket.gethostbyname_ex(socket.gethostname())
        for ip in ip_list:
            if ip:
                addresses.add(ip)
    except OSError:
        pass

    try:
        for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = item[4][0]
            if ip:
                addresses.add(ip)
    except OSError:
        pass

    return addresses


def detect_runtime_profile() -> str:
    profile = os.environ.get('SERVER_PROFILE', '').strip().lower()
    if profile in {'local', 'nas'}:
        return profile

    nas_ip = os.environ.get('NAS_SERVER_IP', '192.168.0.250').strip()
    if nas_ip and nas_ip in _local_ipv4_addresses():
        return 'nas'

    return 'local'


def get_auto_addrport(profile: str) -> str:
    if profile == 'nas':
        return os.environ.get('NAS_RUNSERVER_ADDRPORT', '0.0.0.0:8080').strip() or '0.0.0.0:8080'
    return os.environ.get('LOCAL_RUNSERVER_ADDRPORT', '127.0.0.1:8000').strip() or '127.0.0.1:8000'
