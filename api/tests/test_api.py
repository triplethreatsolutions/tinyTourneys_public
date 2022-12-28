# Stdlib imports
import json
import logging

# Core Django imports
from django.contrib.auth import get_user_model
from django.urls import reverse

# 3rd party app imports
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

# app imports
from subscribers.models import Organization
from subscribers.serializer import *
from event_registration import models as registration_model
from tournaments import models as tournament_model

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


def print_db():
    """
    Print what we have
    """
    for user in User.objects.all():
        print(
            "User: {} {} {} {}".format(
                user.username, user.first_name, user.last_name, user.email
            )
        )


def create_client(user, url, action="", kwargs=None, login=False):
    token = Token.objects.get_or_create(user=user)[0]
    client = APIClient()

    if login:
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        client.login(username=user.username, password=user.password)

    if action == "GET":
        return client.get(url, kwargs=kwargs)
    elif action == "POST":
        return client.post(url, data=kwargs, format="json")
    elif action == "PUT":
        return client.put(url, data=kwargs, format="json")
    elif action == "DELETE":
        return client.delete(url)
    else:
        return 0


class OrganizationAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
        "tournament_location.json",
        "tournament_event.json",
        "tournament_division.json",
        "tournament_team.json",
        "tournament_pool.json",
        "registration_configuration.json",
        "registration_invoice.json",
        "registration_registration.json",
        "registration_question.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.admin = {
            "username": "harry@email.com",
            "first_name": "Harry",
            "last_name": "Potter",
            "email": "harry@email.com",
            "password": "123password!",
            "is_staff": False,
            "is_active": True,
        }

        cls.org_new = {
            "name": "new_organization",
            "accountType": Organization.NEW,
            "admin": cls.admin,
            "primaryPhone": "123-456-7890",
            "secondaryPhone": "098-765-4321",
            "AddressLine1": "123 Street",
            "AddressLine2": "PO Box 123",
            "AddressCity": "city",
            "AddressState": "IA",
            "AddressZIP": "12345",
            "stripeID": "123456789",
        }

        cls.org_update = {
            "name": "update_organization",
            "accountType": Organization.ACTIVE,
            "admin": cls.admin,
            "primaryPhone": "555-555-5555",
            "secondaryPhone": "555-555-5555",
            "AddressLine1": "555 Street",
            "AddressLine2": "PO Box 555",
            "AddressCity": "city",
            "AddressState": "IA",
            "AddressZIP": "55555",
            "stripeID": "55555555",
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_organization_create(self):
        """
        Ensure we can create a new organization object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_organizations")

        response = self.client.post(url, self.org_new, format="json")

        # print(response.status_code, self.__module__, response.data)
        # print_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["admin"]["username"], self.admin["username"])
        self.assertEqual(response.data["admin"]["email"], self.admin["email"])
        self.assertEqual(response.data["name"], self.org_new["name"])
        self.assertEqual(response.data["accountType"], Organization.ACTIVE)
        self.assertEqual(response.data["primaryPhone"], self.org_new["primaryPhone"])
        self.assertEqual(
            response.data["secondaryPhone"], self.org_new["secondaryPhone"]
        )
        self.assertEqual(response.data["AddressLine1"], self.org_new["AddressLine1"])
        self.assertEqual(response.data["AddressLine2"], self.org_new["AddressLine2"])
        self.assertEqual(response.data["AddressZIP"], self.org_new["AddressZIP"])
        self.assertEqual(response.data["stripeID"], self.org_new["stripeID"])

    def test_API_organization_admin_update(self):
        """
        Ensure we can update a organization object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(username="jbowman@tnt5basketball.com")
        org = Organization.objects.get(referenceID="ZLJ031Q5LNR7YO4")

        url = reverse(
            "api:detail_organization", kwargs={"referenceID": org.referenceID}
        )

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.org_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_organization_admin_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_API_organization_director_update(self):
        """
        Ensure we can update a organization object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(username="potter@gmail.com")
        org = Organization.objects.get(referenceID="ZLJ031Q5LNR7YO4")

        url = reverse(
            "api:detail_organization", kwargs={"referenceID": org.referenceID}
        )

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.org_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_organization_director_update_dump.json", "w") as out:
        #    out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_API_organization_director_cannot_update(self):
        """
        Ensure we *cannot* update a organization object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(username="jason.kara.bowman@gmail.com")
        org = Organization.objects.get(referenceID="ZLJ031Q5LNR7YO4")

        url = reverse(
            "api:detail_organization", kwargs={"referenceID": org.referenceID}
        )

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.org_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_organization_director_cannot_update.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RegistrationAPITests(APITestCase):
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
        # runs once before the Test Case runs
        # logger.info('')

        cls.reg_new = {
            "organization": "e8cf688a-c760-4daf-8611-954b95198fd3",
            "invoice": "2be1b75d-16ed-4265-8468-d05b1ea17ec0",
            "event": 1,
            "team": "0a972c84-de56-4a0c-85d5-aa526842799e",
            "registrationStatus": registration_model.Registration.NEW,
            "entryFee": 999.99,
            "disclaimer_accepted": 0,
        }

        cls.reg_update = {
            "organization": "e8cf688a-c760-4daf-8611-954b95198fd3",
            "invoice": "2be1b75d-16ed-4265-8468-d05b1ea17ec0",
            "event": 1,
            "team": "0a972c84-de56-4a0c-85d5-aa526842799e",
            "registrationStatus": registration_model.Registration.COMPLETED,
            "entryFee": 555.55,
            "disclaimer_accepted": 1,
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_registration_create(self):
        """
        Ensure we can create a new registration object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_registrations")

        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        response = create_client(
            user, url, action="POST", kwargs=self.reg_new, login=True
        )

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # uid.urn returns string value
        self.assertEqual(
            response.data["organization"].urn[9:], self.reg_new["organization"]
        )
        # uid.urn returns string value
        self.assertEqual(response.data["invoice"].urn[9:], self.reg_new["invoice"])
        self.assertEqual(response.data["event"], self.reg_new["event"])
        # uid.urn returns string value
        self.assertEqual(response.data["team"].urn[9:], self.reg_new["team"])
        self.assertEqual(
            response.data["registrationStatus"], registration_model.Registration.DRAFT
        )
        # DRF sets COERCE_DECIMAL_TO_STRING to True by default, casting to float to test actual input
        self.assertEqual(float(response.data["entryFee"]), self.reg_new["entryFee"])

    def test_API_registration_update(self):
        """
        Ensure we can update a registration object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab registration loaded from fixture
        reg = registration_model.Registration.objects.get(
            pk="d262f505-5ba5-42e1-8012-ab0d189f126d"
        )

        url = reverse(
            "api:detail_registration", kwargs={"referenceID": reg.referenceID}
        )

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.reg_update, login=True
        )

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["referenceID"], reg.referenceID)
        self.assertEqual(float(response.data["entryFee"]), self.reg_update["entryFee"])
        self.assertEqual(
            response.data["registrationStatus"], self.reg_update["registrationStatus"]
        )
        self.assertEqual(response.data["event"], self.reg_update["event"])
        self.assertEqual(response.data["organization"], reg.organization_id)
        self.assertEqual(response.data["invoice"], reg.invoice_id)
        self.assertEqual(
            response.data["disclaimer_accepted"], self.reg_update["disclaimer_accepted"]
        )


class TeamAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
        "tournament_staff.json",
        "tournament_location.json",
        "tournament_event.json",
        "tournament_division.json",
        "tournament_team.json",
        "tournament_pool.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.team_new = {
            "name": "Test Team",
            "gender": "U",
            "ageGroup": "Mixed",
            "event": 2,
            "division": 1,
        }

        cls.team_update = {
            "name": "Update Team",
            "gender": "M",
            "ageGroup": "College",
            "event": 1,
            "division": 2,
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_team_create(self):
        """
        Ensure we can create a new team object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_teams")

        response = self.client.post(url, self.team_new, format="json")

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_team_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_team_update(self):
        """
        Ensure we can update a team object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab team loaded from fixture
        team = tournament_model.Team.objects.get(
            pk="0a972c84-de56-4a0c-85d5-aa526842799e"
        )

        url = reverse("api:detail_team", kwargs={"pk": team.pk})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.team_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_team_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StaffAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
        "tournament_location.json",
        "tournament_staff.json",
        "tournament_event.json",
        "tournament_division.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.staff_new = {
            "staff_type": 1,
            "first_name": "Assistant",
            "last_name": "Coach",
            "email": "assistantcoach@mail.com",
            "primary_phone": "123-456-7890",
            "secondary_phone": "123-456-7890",
            "address_line1": "123 Street",
            "address_line2": "PO Box 123",
            "address_city": "City",
            "address_state": "IA",
            "address_zip": "12345",
        }

        cls.staff_update = {
            "staff_type": 2,
            "first_name": "Director",
            "last_name": "Coach",
            "email": "directorcoach@mail.com",
            "primary_phone": "123-456-7890",
            "secondary_phone": "123-456-7890",
            "address_line1": "123 Street",
            "address_line2": "PO Box 123",
            "address_city": "City",
            "address_state": "IA",
            "address_zip": "12345",
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_staff_create(self):
        """
        Ensure we can create a new staff object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_staff")

        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        response = create_client(
            user, url, action="POST", kwargs=self.staff_new, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_staff_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_staff_update(self):
        """
        Ensure we can update a staff object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab team loaded from fixture
        staff = tournament_model.Staff.objects.get(
            staffID="ee790dd8-044d-400c-8b96-23abb63cdfb0"
        )

        url = reverse("api:detail_staff", kwargs={"pk": staff.pk})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.staff_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_staff_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InvoiceAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "subscriber_organization.json",
        "tournament_location.json",
        "registration_invoice.json",
        "tournament_event.json",
        "tournament_division.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.invoice_new = {
            "purchaseOrderID": "0",
            "billingInfo": None,
            "invoiceStatus": registration_model.Invoice.DRAFT,
            "amountDue": "999.99",
            "amountPaid": "999.99",
            "processingFee": "99.00",
            "taxes": "99.00",
            "paymentMethod": 0,
        }

        cls.invoice_update = {
            # "referenceID": 0,  # Must set, referenceID cannot be NULL
            "billingInfo": None,
            "invoiceStatus": registration_model.Invoice.PAID,
            "amountDue": "555.55",
            "amountPaid": "555.55",
            "processingFee": "55.00",
            "taxes": "55.00",
            "paymentMethod": 100,
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_invoice_create(self):
        """
        Ensure we can create a new invoice object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_invoices")

        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        response = create_client(
            user, url, action="POST", kwargs=self.invoice_new, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_invoice_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_invoice_update(self):
        """
        Ensure we can update a invoice object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab invoice loaded from fixture
        invoice = registration_model.Invoice.objects.get(
            invoiceID="2be1b75d-16ed-4265-8468-d05b1ea17ec0"
        )

        url = reverse("api:detail_invoice", kwargs={"referenceID": invoice.referenceID})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.invoice_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_invoice_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ConfigurationAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "tournament_location.json",
        "registration_configuration.json",
        "tournament_event.json",
        "tournament_division.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.config_new = {
            "event": 2,
            "registrationState": 1,
            "entryFee": "999.99",
            "start_date": "2020-04-11",
            "end_date": "2020-04-12",
            "info": "Test registration info",
            "disclaimerEnabled": True,
            "disclaimer": "This is tournament disclaimer",
            "questionsEnabled": True,
            "numberOfQuestions": 10,
            "promoEnabled": True,
            "promoCode": "123promo",
            "promoValue": "999.99",
        }

        cls.config_update = {
            "event": 1,
            "registrationState": 2,
            "entryFee": "555.55",
            "start_date": "2020-04-11",
            "end_date": "2020-04-12",
            "info": "Updated test info",
            "disclaimerEnabled": False,
            "disclaimer": "This is updated disclaimer",
            "questionsEnabled": False,
            "numberOfQuestions": 5,
            "promoEnabled": False,
            "promoCode": "123updated",
            "promoValue": "555.55",
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_configuration_create(self):
        """
        Ensure we can create a new configuration object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_configurations")

        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        response = create_client(
            user, url, action="POST", kwargs=self.config_new, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_configuration_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_configuration_update(self):
        """
        Ensure we can update a configuration object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab invoice loaded from fixture
        config = registration_model.Configuration.objects.get(event_id=1)

        url = reverse("api:detail_configuration", kwargs={"pk": config.event_id})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.config_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_configuration_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "tournament_location.json",
        "registration_configuration.json",
        "registration_question.json",
        "tournament_event.json",
        "tournament_division.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.q_new = {
            "configuration": 1,
            "question": "This is an api test question?",
            "priority": 1,
        }

        cls.q_update = {
            "configuration": 1,
            "question": "This is an updated question?",
            "priority": 9,
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_question_create(self):
        """
        Ensure we can create a new question object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_questions")

        response = self.client.post(url, self.q_new, format="json")

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_question_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_question_update(self):
        """
        Ensure we can update a question object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab invoice loaded from fixture
        q = registration_model.Question.objects.get(configuration=1)

        url = reverse("api:detail_question", kwargs={"pk": q.pk})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.q_update, login=True
        )

        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_question_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnswerAPITests(APITestCase):
    fixtures = [
        "customusers.json",
        "tournament_location.json",
        "registration_configuration.json",
        "registration_question.json",
        "tournament_event.json",
        "tournament_division.json",
        "tournament_team.json",
        "tournament_pool.json",
        "registration_registration",
        "registration_invoice.json",
        "registration_answer.json",
        "subscriber_organization.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # runs once before the Test Case runs
        # logger.info('')

        cls.a_new = {
            "registration": "d262f505-5ba5-42e1-8012-ab0d189f126d",
            "question": 1,
            "answer": "Hope this is a good test answer.",
        }

        cls.a_update = {
            "registration": "d262f505-5ba5-42e1-8012-ab0d189f126d",
            "question": 1,
            "answer": "This is an updated answer.",
        }

    def setUp(self):
        # setUp runs before every test
        pass

    def test_API_answer_create(self):
        """
        Ensure we can create a new answer object.
        """
        logger.info("")
        # namespace for reverse urls is 'api'
        url = reverse("api:list_answers")

        response = self.client.post(url, self.a_new, format="json")

        # Convert UUID field to string
        temp = response.data["registration"].urn[9:]
        response.data["registration"] = temp
        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_answer_create_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_API_answer_update(self):
        """
        Ensure we can update a answer object.

        """
        logger.info("")
        # Grab user loaded from fixture
        user = User.objects.get(pk=1)

        # Grab invoice loaded from fixture
        a = registration_model.Answer.objects.get(pk=1)

        url = reverse("api:detail_answer", kwargs={"pk": a.pk})

        # Update request
        response = create_client(
            user, url, action="PUT", kwargs=self.a_update, login=True
        )

        # Convert UUID field to string
        temp = response.data["registration"].urn[9:]
        response.data["registration"] = temp
        # dump response data to file for analysis
        # data = json.dumps(response.data, indent=4)
        # with open("test_fixtures/" + "test_API_answer_update_dump.json", "w") as out:
        #     out.write(data)

        # print(response.status_code, self.__module__, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
