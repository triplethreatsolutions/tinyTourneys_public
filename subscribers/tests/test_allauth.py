# std imports
import logging

# django imports
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

# 3rd party imports
from allauth.account.auth_backends import AuthenticationBackend
from allauth.account import app_settings

# app imports
from django.urls import reverse

from subscribers.models import *

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


class AuthenticationBackendTests(TestCase):
    fixtures = ["customusers.json"]

    def setUp(self):
        user = User.objects.get(pk=1)
        self.user = user

    # def test_login_page_login_without_verification(self):
    #     response = self.client.post(
    #         'rest-auth/login/',
    #         {
    #             'login': 'jbowman@tnt5basketball.com',
    #             'password': 'Iowaprep1!',
    #         }
    #     )
    #
    #     self.assertRedirects(response, '/dashboard/')
