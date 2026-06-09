from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    role_chooice = (

        ('admin','Admin'),
        ('head_teacher','Head_Teacher'),
        ('teacher','teacher'),
        ('student','Student')
    )
    role = models.CharField(max_length=50, choices=role_chooice, default='student')
    profile_image = models.ImageField(upload_to='profile/',null=True,blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    





class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)        
    


    