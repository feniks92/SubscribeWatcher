import os
from base64 import b64decode, b64encode
from hashlib import blake2b, pbkdf2_hmac

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from libs.config import settings

SALT = settings.get('CRYPT', {}).get('SECRET', 'dummy_salt').encode()
SALT_HASH = blake2b(SALT, digest_size=32).digest()
AES_INITIAL_VECTOR_SIZE = 16
PADDER = padding.PKCS7(128)


def encrypt(str_: str) -> str:
    input_vector = os.urandom(AES_INITIAL_VECTOR_SIZE)
    cipher = Cipher(algorithms.AES(SALT_HASH), modes.CBC(input_vector))
    encryptor = cipher.encryptor()
    padder = PADDER.padder()
    ciphertext = encryptor.update(padder.update(str_.encode()) + padder.finalize()) + encryptor.finalize()
    return b64encode(input_vector + ciphertext).decode('utf-8')


def decrypt(str_: str) -> str:
    decoded_str = b64decode(str_)
    input_vector = decoded_str[:AES_INITIAL_VECTOR_SIZE]
    ciphertext = decoded_str[AES_INITIAL_VECTOR_SIZE:]
    cipher = Cipher(algorithms.AES(SALT_HASH), modes.CBC(input_vector))
    decryptor = cipher.decryptor()
    unpadder = PADDER.unpadder()
    result = unpadder.update(decryptor.update(ciphertext) + decryptor.finalize()) + unpadder.finalize()
    return result.decode('utf-8')


def hash_key(input_value: str) -> str:
    return blake2b(input_value.encode(), digest_size=32).hexdigest()


def secure_hash_key(input_value: str,
                    hash_iterations_count: int = 100000,
                    salt: str = SALT) -> str:
    """
    Use this function very carefully, it creates high cpu load.
    Usefully for passwords or other critical personal information
    https://python-scripts.com/haslib-pbkdf2-check-password
    """
    return pbkdf2_hmac('sha256', input_value.encode(), salt, hash_iterations_count).hex()
