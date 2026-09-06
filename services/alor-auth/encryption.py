from cryptography.fernet import Fernet


def encrypt_token(key: str, value: str) -> str:
    return Fernet(key).encrypt(value.encode()).decode()


def decrypt_token(key: str, value: str) -> str:
    return Fernet(key).decrypt(value.encode()).decode()
