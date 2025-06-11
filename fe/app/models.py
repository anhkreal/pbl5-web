from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    raspberry_ip = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class Insect(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  # Tên tiếng Việt
    scientific_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    habitat = models.TextField(blank=True)
    host_plants = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    active_season = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.BinaryField(blank=True, null=True)  # Lưu blob

    def __str__(self):
        return self.name

class ImageHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insect = models.ForeignKey(Insect, on_delete=models.SET_NULL, null=True)
    image = models.BinaryField(blank=True, null=True)  # Lưu blob
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.insect} - {self.detected_at.strftime('%Y-%m-%d %H:%M')}"
