'''
Database models.
'''
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

def recipe_image_file_path(instance, filename):
    #Generate filepath for new recipe image
    ext = os.path.splitext(filename)[1]    #removing extension
    filename = f'{uuid.uuid4()}{ext}' #create new file name and then add back extension used

    return os.path.join('uploads', 'recipe', filename)

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

class Recipe(models.Model):
    #Recipe Object
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name