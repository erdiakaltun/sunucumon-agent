import uuid
import socket

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import os

def get_mac():
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = ':'.join(mac_num[i:i+2] for i in range(0, 12, 2))
    return mac

def get_hostname():
    return socket.gethostname()

# --- AES Şifreleme Fonksiyonları ---

def derive_key(secret):
    # 32 byte key için SHA256 hash al
    return hashlib.sha256(secret.encode()).digest()

def encrypt_aes(plaintext, secret):
    key = derive_key(secret)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode()

def decrypt_aes(ciphertext_b64, secret):
    key = derive_key(secret)
    data = base64.b64decode(ciphertext_b64.encode())
    iv = data[:16]
    ct = data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    pt = decryptor.update(ct) + decryptor.finalize()
    return pt.decode()
