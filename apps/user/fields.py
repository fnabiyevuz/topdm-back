from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


class EncryptedTextField(models.TextField):
    def get_prep_value(self, value):
        if value is None:
            return value
        f = Fernet(settings.SECRET_ENCRYPTION_KEY.encode())
        return f.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            f = Fernet(settings.SECRET_ENCRYPTION_KEY.encode())
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value
