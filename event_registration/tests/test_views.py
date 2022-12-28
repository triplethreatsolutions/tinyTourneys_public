# std imports
import logging

# django imports
from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve

# 3rd party imports


# app imports
from tournaments.models import Event
from event_registration.views import *

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RegistrationTests(TestCase):

    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
        "tournament_staff.json",
        "tournament_location.json",
        "tournament_team.json",
        "tournament_pool.json",
        "tournament_event.json",
        "tournament_division.json",
        "registration_configuration.json",
        "registration_invoice.json",
        "registration_registration.json",
        "registration_question.json",
    ]

    @classmethod
    def setUpTestData(cls):
        event = Event.objects.get(pk=1)
        cls.url = reverse(
            "event_registration:registration_register", kwargs={"slug": event.slug}
        )

    def setUp(self):
        self.response = self.client.get(self.url)

    def test_registration_status_code(self):
        logger.info("")
        self.assertEqual(self.response.status_code, 200)

    def test_registration_url_resolves_registration_view(self):
        logger.info("")
        view = resolve(self.url)
        self.assertEqual(view.func.__name__, registration_register_view.__name__)

    def test_registration_template(self):
        logger.info("")
        self.assertTemplateUsed(self.response, "event_registration/register.html")

    def test_registration_contains_correct_html(self):
        logger.info("")
        self.assertContains(self.response, "Team Registration", status_code=200)

    def test_registration_does_not_contain_incorrect_html(self):
        logger.info("")
        self.assertNotContains(
            self.response, "I should not be on this page", status_code=200
        )
