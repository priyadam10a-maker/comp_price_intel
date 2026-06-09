from django.db import models

# Create your models here.
class User(models.Model):
    user_id=models.AutoField(primary_key=True)
    full_name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    password_hash=models.CharField(max_length=255)
    role=models.CharField(max_length=20,default='Analyst')
    last_login=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField()
    class Meta:
        db_table='users'
        managed=False