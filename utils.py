import socket
import uuid

def get_mac():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac

def get_hostname():
    return socket.gethostname()
