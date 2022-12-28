# Stdlib imports
import logging

# Core Django imports
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings


# Third-party app imports

# Imports from app
from settings.development import *

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create your tests here.


class ContactTestCase(TestCase):
    def setUp(self):
        """Setting up Contact Tests"""

    # @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_Contact_Send_Email(self):
        """
        Verify We Can Send Emails
        """

        logger.info("")

        success = mail.send_mail(
            "Test Subject Header",
            "This is a test message.",
            DEFAULT_FROM_EMAIL,
            ADMINS,
            fail_silently=False,
        )

        self.assertEqual(success, 1, "Send Email Was Successful")
