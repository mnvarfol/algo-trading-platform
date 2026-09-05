from dataclasses import dataclass


@dataclass
class Config:
    auth_url: str = "https://oauth.alor.ru/refresh"
    http_url: str = "https://api.alor.ru"
