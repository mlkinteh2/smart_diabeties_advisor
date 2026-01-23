from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Patient: {self.user.username}"

    @property
    def get_initials(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0].upper()}{self.user.last_name[0].upper()}"
        elif self.user.first_name:
            return self.user.first_name[0].upper()
        elif self.user.last_name:
            return self.user.last_name[0].upper()
        return self.user.username[0].upper()


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Dr. {self.user.username}"
