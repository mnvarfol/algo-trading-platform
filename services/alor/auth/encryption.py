from cryptography.fernet import Fernet


def encrypt_token(fernet: Fernet, value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_token(fernet: Fernet, value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
