from django.contrib.auth.models import User
import pytest
from rest_framework.test import APIClient

# we define fixtures that are going to be used across test modules
@pytest.fixture  # by using this. this function is reusable piece of code and we can add it to out tests as a parameter. This reduce redundancy.
def api_client():
  return APIClient()

@pytest.fixture
def authenticate(api_client):
  def do_authenticate(is_staff=False):
    return api_client.force_authenticate(user=User(is_staff=is_staff))
  return do_authenticate