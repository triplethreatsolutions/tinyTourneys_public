# std imports
import logging

# django imports
from django.test import SimpleTestCase, TestCase
from django.urls import resolve

# 3rd party imports
from allauth.account.views import *
from allauth.account.forms import *

# app imports
from subscribers import forms

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("account_login")

    def setUp(self):
        self.response = self.client.get(self.url)

    def test_login_status_code(self):
        logger.info("")
        self.assertEqual(self.response.status_code, 200)

    def test_login_url_resolves_login_view(self):
        logger.info("")
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, login.__name__)

    def test_login_template(self):
        logger.info("")
        self.assertTemplateUsed(self.response, "account/login.html")

    def test_login_form(self):
        logger.info("")
        form = self.response.context.get("form")
        self.assertIsInstance(form, LoginForm)
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_login_contains_correct_html(self):
        logger.info("")
        self.assertContains(self.response, "Forgot Password?", status_code=200)

    def test_login_does_not_contain_incorrect_html(self):
        logger.info("")
        self.assertNotContains(
            self.response, "I should not be on this page", status_code=200
        )


class SignUpTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("account_signup")

    def setUp(self):
        self.response = self.client.get(self.url)

    def test_signup_status_code(self):
        logger.info("")
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        logger.info("")
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, signup.__name__)

    def test_signup_template(self):
        logger.info("")
        self.assertTemplateUsed(self.response, "account/signup.html")

    def test_signup_form(self):
        logger.info("")
        form = self.response.context.get("form")
        self.assertIsInstance(form, forms.SubscriberForm)
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_signup_contains_correct_html(self):
        logger.info("")
        self.assertContains(self.response, "Create Your Account", status_code=200)

    def test_signup_does_not_contain_incorrect_html(self):
        logger.info("")
        self.assertNotContains(
            self.response, "I should not be on this page", status_code=200
        )
