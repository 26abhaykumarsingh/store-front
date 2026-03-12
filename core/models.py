from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class User(AbstractUser):
  # pass # we should always create a ingerited user model even if we don't need to make any changes to auth user model, so we dont get difficulty in creating it mid project; if we create it mid project we have to drop the database and then recreate it again, which is a pain
  email = models.EmailField(unique=True)




# to inherit another user first we extend the AbstractUser modal then we in settings.py add this "AUTH_USER_MODEL = 'core.User'" then we never user user directly but as settings.AUTH_USER_MODEL