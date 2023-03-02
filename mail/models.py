from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta


class OTP(models.Model):
    choice = [
        ("PH", "phone"),
        ("EM", "email")
    ]
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    time = models.DateTimeField(auto_now_add=datetime.now())
    type = models.CharField(max_length=10, choices=choice)

    @property
    def exp_time(self):
        return self.time + timedelta(minutes=10)


class CustomUser(AbstractUser):
    email_is_verified = models.BooleanField(default=False)
    phone_is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=11)
