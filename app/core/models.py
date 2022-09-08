'''
Database models.
'''

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)



class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        #create, save, and return a new user.
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password) #encrypts password. 
        user.save(using=self._db)
        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    #Custom user class representing user in the database

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() #assigns a UserManager to User class

    USERNAME_FIELD = 'email'

