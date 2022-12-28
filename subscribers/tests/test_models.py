# std imports
import logging

# django imports
from django.contrib.auth import get_user_model
from django.test import TestCase

# app imports
from subscribers import models

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


class InterestedEmailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass
        # logger.info('')

    def test_create_interested_email(self):
        logger.info("")
        email = models.InterestedEmail.objects.create(email="testuser@mail.com")

        self.assertEqual(email.email, "testuser@mail.com")


class OrganizationTests(TestCase):
    fixtures = ["customusers.json"]

    @classmethod
    def setUpTestData(cls):
        pass
        # logger.info('')

    def test_create_organization(self):
        logger.info("")
        # user object created using fixtures
        user = User.objects.get(pk=1)
        org = models.Organization.objects.create(
            name="test_organization",
            accountType=models.Organization.NEW,
            admin=user,
            primaryPhone="123-456-7890",
            secondaryPhone="098-765-4321",
            AddressLine1="123 Street",
            AddressLine2="PO Box 123",
            AddressCity="city",
            AddressState="IA",
            AddressZIP="12345",
            stripeID="123456789",
        )
        org.directors.add(user)
        org.save()

        self.assertEqual(org.admin.email, user.email)
        self.assertEqual(org.name, "test_organization")
        self.assertEqual(org.accountType, models.Organization.ACTIVE)
        self.assertEqual(org.primaryPhone, "123-456-7890")
        self.assertEqual(org.secondaryPhone, "098-765-4321")
        self.assertEqual(org.AddressLine1, "123 Street")
        self.assertEqual(org.AddressLine2, "PO Box 123")
        self.assertEqual(org.AddressCity, "city")
        self.assertEqual(org.AddressState, "IA")
        self.assertEqual(org.AddressZIP, "12345")
