from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


class EncryptedTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.fernet = Fernet(settings.SECRET_ENCRYPTION_KEY.encode())
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        # Double-encrypt bo‘lishini oldini olish
        try:
            self.fernet.decrypt(value.encode())
            return value  # Allaqachon encrypt qilingan
        except (InvalidToken, ValueError):
            return self.fernet.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return value  # Agar decrypt bo‘lmasa, shunchaki qaytaradi

    def to_python(self, value):
        if value is None:
            return value
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except (InvalidToken, AttributeError):
            return value
