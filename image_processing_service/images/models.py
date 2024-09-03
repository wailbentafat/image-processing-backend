from django.contrib.auth.models import User
from django.db import models

class image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    size=models.IntegerField(default=0)
    format=models.CharField(max_length=10,blank=True,default='')
    
    
    