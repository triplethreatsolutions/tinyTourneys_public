# event_registration/tests/test_models.py
# std imports
import logging

# core django imports
from django.contrib.auth import get_user_model
from django.test import TestCase

from event_registration.models import *

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


class RegistrationTests(TestCase):
    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
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
        # logger.info('')

        # Grab user loaded by fixture
        cls.user = User.objects.get(pk=1)

    def test_create_invoice(self):
        logger.info("")
        invoice = Invoice.objects.create(
            invoiceStatus=0,
            amountDue=9999.99,
            amountPaid=9999.99,
            processingFee=9999.99,
            taxes=9999.99,
            paymentMethod=100,
        )

        self.assertEqual(invoice.invoiceStatus, 1)
        self.assertEqual(invoice.amountDue, 9999.99)
        self.assertEqual(invoice.amountPaid, 9999.99)
        self.assertEqual(invoice.processingFee, 9999.99)
        self.assertEqual(invoice.taxes, 9999.99)
        self.assertEqual(invoice.paymentMethod, 100)
        self.assertRegex(invoice.purchaseOrderID, r"^TT")

    def test_create_billing_info(self):
        logger.info("")
        billinfo = BillingInfo.objects.create(
            first_name="harry",
            last_name="potter",
            email="potter@gmail.com",
            primary_phone="123-456-7890",
            secondary_phone="098-765-4321",
            address_line1="123 Street",
            address_line2="PO Box 123",
            address_city="city",
            address_state="IA",
            address_zip="12345",
        )

        self.assertEqual(billinfo.first_name, "harry")
        self.assertEqual(billinfo.last_name, "potter")
        self.assertEqual(billinfo.email, "potter@gmail.com")
        self.assertEqual(billinfo.primary_phone, "123-456-7890")
        self.assertEqual(billinfo.secondary_phone, "098-765-4321")
        self.assertEqual(billinfo.address_line1, "123 Street")
        self.assertEqual(billinfo.address_line2, "PO Box 123")
        self.assertEqual(billinfo.address_city, "city")
        self.assertEqual(billinfo.address_state, "IA")
        self.assertEqual(billinfo.address_zip, "12345")

    def test_create_configuration(self):
        logger.info("")
        date = "2021-05-20"
        # Get event loaded by fixture
        event = Event.objects.get(pk=2)

        config = Configuration.objects.create(
            event=event,
            registrationState=1,
            entryFee=999.99,
            start_date=date,
            end_date=date,
            info="registration info",
            disclaimerEnabled=True,
            disclaimer="disclaimer message",
            questionsEnabled=True,
            numberOfQuestions=10,
            promoEnabled=True,
            promoCode="promo123",
            promoValue=999.99,
        )

        # self.assertEqual(config.event_id, event.id)
        self.assertEqual(config.registrationState, 1)
        self.assertEqual(config.entryFee, 999.99)
        self.assertEqual(config.start_date, date)
        self.assertEqual(config.end_date, date)
        self.assertEqual(config.info, "registration info")
        self.assertEqual(config.disclaimerEnabled, True)
        self.assertEqual(config.disclaimer, "disclaimer message")
        self.assertEqual(config.questionsEnabled, True)
        self.assertEqual(config.numberOfQuestions, 10)
        self.assertEqual(config.promoEnabled, True)
        self.assertEqual(config.promoCode, "promo123")
        self.assertEqual(config.promoValue, 999.99)

    def test_create_question(self):
        logger.info("")
        # Grab configuration loaded by fixture
        config = Configuration.objects.get(pk=1)

        question = Question.objects.create(
            configuration=config,
            question="This is a test question",
            priority=1,
        )

        self.assertEqual(question.configuration, config)
        self.assertEqual(question.question, "This is a test question")
        self.assertEqual(question.priority, 1)

    def test_create_answer(self):
        logger.info("")
        # Grab registration loaded by fixture
        reg = Registration.objects.get(pk="d262f505-5ba5-42e1-8012-ab0d189f126d")
        # Grab question loaded by fixture
        question = Question.objects.get(pk=1)

        answer = Answer.objects.create(
            registration=reg,
            question=question,
            answer="Please schedule this test later",
        )

        self.assertEqual(answer.registration, reg)
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.answer, "Please schedule this test later")
