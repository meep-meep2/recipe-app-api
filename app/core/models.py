'''
Database models.
'''

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        #create, save, and return a new user.
        
        if not email:
            raise ValueError('User must have email address')

        #Normalizing email. Could also just use self.normaliz_email(email) which is provided by BaseUserManager.
        a, b = email.split('@')
        b = b.casefold()

        user = self.model(email= ("{}@{}".format(a,b)), **extra_fields)

        user.set_password(password) #encrypts password. 
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password):
        #Create and return new superuser

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True #from Permissions mixin
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

