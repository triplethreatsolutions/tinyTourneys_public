# std imports
import uuid
import logging

# Core Django imports
from django.db import models

# 3rd party import
from hashid_field import HashidField

# app imports
from common.models import TimeStampedModel
from common.utils import unique_id_gen, unique_hash_gen
from tournaments.models import Event, Division, Staff, Team
from subscribers.models import Organization

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create your models here.

STATES = (
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "Dist. of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
)


class Registration(TimeStampedModel):
    NEW = 10
    DRAFT = 99
    COMPLETED = 1
    DELETED = -1

    REGISTRATION_STATUS_OPTIONS = (
        (NEW, "new"),
        (DRAFT, "draft"),
        (COMPLETED, "completed"),
        (DELETED, "deleted"),
    )

    registrationID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=False
    )
    referenceID = HashidField(
        blank=True, min_length=15, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    # TODO: Change related name to the plural word "registrations"
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.CASCADE,
        null=True,
        related_name="registration_invoice",
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, related_name="registration_event"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, related_name="registration_team"
    )

    registrationStatus = models.IntegerField(
        blank=False, choices=REGISTRATION_STATUS_OPTIONS, default=0
    )

    entryFee = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    comments = models.CharField(max_length=200, blank=True)

    disclaimer_accepted = models.BooleanField()

    def __str__(self):
        return (
            self.event.title + "-" + self.team.name + " ($" + str(self.entryFee) + ")"
        )

    def save(self, *args, **kwargs):
        if self.registrationStatus == self.NEW:
            self.registrationStatus = self.DRAFT
            new_hash = False
            while not new_hash:
                unique_hash = unique_hash_gen()
                if not Registration.objects.filter(referenceID=unique_hash).exists():
                    new_hash = True
                    self.referenceID = unique_hash
                else:
                    logger.info("unique_hash_gen() crash detected: %s" % unique_hash)

        super(Registration, self).save(
            *args, **kwargs
        )  # Call the "real" save() method.


class Invoice(TimeStampedModel):
    OPEN = 1
    OVERDUE = -1
    PARTIAL = 2
    SENT = 10
    VOID = -100
    DRAFT = 0
    PAID = 1000
    VIEWED = 100

    INVOICE_STATUS_OPTIONS = (
        (OPEN, "open"),
        (OVERDUE, "overdue"),
        (PARTIAL, "partial"),
        (SENT, "sent"),
        (VOID, "void"),
        (DRAFT, "draft"),
        (PAID, "paid"),
        (VIEWED, "viewed"),
    )

    PAYMENT_METHOD_OPTIONS = (
        (0, "cash"),
        (10, "check"),
        (100, "credit card"),
    )

    # TODO: Remove camelCase variable naming

    invoiceID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=False
    )
    purchaseOrderID = models.CharField(max_length=100, blank=True)
    referenceID = HashidField(
        blank=True, min_length=15, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    )
    billingInfo = models.ForeignKey(
        "BillingInfo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="invoice_billinginfo",
    )

    invoiceStatus = models.IntegerField(
        blank=False, choices=INVOICE_STATUS_OPTIONS, default=0
    )

    amountDue = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    amountPaid = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    processingFee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    taxes = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    paymentMethod = models.IntegerField(
        blank=False, choices=PAYMENT_METHOD_OPTIONS, default=0
    )

    def save(self, *args, **kwargs):
        if self.invoiceStatus == self.DRAFT:
            self.invoiceStatus = self.OPEN
            new_id = False
            while not new_id:
                unique_id = unique_id_gen()
                if not Invoice.objects.filter(purchaseOrderID=unique_id).exists():
                    new_id = True
                    self.purchaseOrderID = unique_id
                else:
                    logger.info("unique_id_gen() crash detected: %s" % unique_id)

            new_hash = False
            while not new_hash:
                unique_hash = unique_hash_gen()
                if not Invoice.objects.filter(referenceID=unique_hash).exists():
                    new_hash = True
                    self.referenceID = unique_hash
                else:
                    logger.info("unique_hash_gen() crash detected: %s" % unique_hash)

        super(Invoice, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return self.referenceID.hashid


class BillingInfo(TimeStampedModel):
    billingID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=False
    )

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(null=True)
    primary_phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True)

    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100)
    address_state = models.CharField(max_length=50, choices=STATES)
    address_zip = models.CharField(max_length=20)

    def __str__(self):
        return self.first_name + "" + self.last_name


NUMBER_OF_QUESTIONS = (
    (1, "1 Question"),
    (2, "2 Questions"),
    (3, "3 Questions"),
    (4, "4 Questions"),
    (5, "5 Questions"),
    (6, "6 Questions"),
    (7, "7 Questions"),
    (8, "8 Questions"),
    (9, "9 Questions"),
    (10, "10 Questions"),
)


class Configuration(TimeStampedModel):

    REGISTRATION_STATE = ((0, "Off"), (1, "On"), (2, "Paused"))

    event = models.OneToOneField(
        Event, primary_key=True, on_delete=models.CASCADE, null=False
    )

    registrationState = models.IntegerField(default=0, choices=REGISTRATION_STATE)

    entryFee = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    start_date = models.DateField("Start Date", blank=True)
    end_date = models.DateField("End Date", blank=True)

    info = models.TextField(blank=True, null=True)

    # TODO: should include a many-to-many field for questions attached to this configuration
    # questions = models.ManyToManyField('Question', blank=True, related_name='configurations')

    disclaimerEnabled = models.BooleanField(default=False)
    disclaimer = models.TextField(blank=True, null=True)

    questionsEnabled = models.BooleanField(default=False)
    numberOfQuestions = models.PositiveIntegerField(
        blank=False, choices=NUMBER_OF_QUESTIONS, default=1
    )

    promoEnabled = models.BooleanField(default=False)
    promoCode = models.CharField(max_length=25, blank=True, null=True)
    promoValue = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def display_start_date(self):
        return self.start_date.strftime("%Y-%m-%d")

    def display_end_date(self):
        return self.end_date.strftime("%Y-%m-%d")

    def __str__(self):
        return self.event.title


class Question(TimeStampedModel):
    configuration = models.ForeignKey(
        Configuration, on_delete=models.CASCADE, null=True
    )
    question = models.CharField(max_length=100, blank=False, null=False)
    priority = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question[0:30]


class Answer(TimeStampedModel):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.answer[0:30]
