# std imports
from __future__ import unicode_literals
import uuid
import logging

# django imports
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# 3rd party imports
from hashid_field import HashidField
from rest_framework.authtoken.models import Token

# App imports
from common.utils import unique_hash_gen, activation_code_gen
from common.models import TimeStampedModel

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

User = get_user_model()

# Organization model.


class InterestedEmail(TimeStampedModel):

    email = models.EmailField("email address", blank=True)

    def __str__(self):
        return self.email


class Organization(TimeStampedModel):
    NEW = 99
    ACTIVE = 1
    CLOSED = -1
    PAST_DUE = 2
    BANNED = -100
    FREE = 0
    SUPER_ADMIN = 1000
    BETA = 100

    ACCOUNT_TYPE_OPTIONS = (
        (NEW, "new"),
        (ACTIVE, "active"),
        (CLOSED, "closed"),
        (PAST_DUE, "past due"),
        (BANNED, "banned"),
        (SUPER_ADMIN, "superadmin"),
        (BETA, "beta"),
    )

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

    organizationID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, blank=False
    )
    referenceID = HashidField(
        blank=True, min_length=15, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    )

    name = models.CharField(max_length=100, blank=True)

    accountType = models.IntegerField(
        blank=False, choices=ACCOUNT_TYPE_OPTIONS, default=NEW
    )
    activationCode = models.IntegerField(blank=True, default=0)

    directors = models.ManyToManyField(
        User, blank=False, related_name="organization_directors"
    )
    # related name allow us to use user.organization_admin.all() to find all orgs related to user
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="organization_admin"
    )

    primaryPhone = models.CharField(max_length=20, null=True, blank=True)
    secondaryPhone = models.CharField(max_length=20, null=True, blank=True)

    AddressLine1 = models.CharField(max_length=100, blank=True)
    AddressLine2 = models.CharField(max_length=100, blank=True)
    AddressCity = models.CharField(max_length=100, blank=True)
    AddressState = models.CharField(max_length=50, choices=STATES, blank=True)
    AddressZIP = models.CharField(max_length=20, blank=True)

    stripeID = models.CharField(max_length=30, blank=True)
    stripe_details_submitted = models.BooleanField(default=False)
    stripe_charges_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_directors(self):
        return self.directors.all()

    def save(self, *args, **kwargs):
        # Only create activation code and reference ID if account is NEW
        if self.accountType == self.NEW:
            self.accountType = self.ACTIVE
            self.activationCode = activation_code_gen()
            logger.info(
                "Subscriber Activation: %s:  Code: %s"
                % (self.name, self.activationCode)
            )
            logger.info(
                "Subscriber referenceID: %s:  ID: %s" % (self.name, self.referenceID)
            )
            new_hash = False
            while not new_hash:
                unique_hash = unique_hash_gen()
                if not Organization.objects.filter(referenceID=unique_hash).exists():
                    new_hash = True
                    self.referenceID = unique_hash
                else:
                    logger.info(
                        "unique_hash_gen() crash detected: %s   Hash: %s"
                        % (self.name, unique_hash)
                    )

        super(Organization, self).save(
            *args, **kwargs
        )  # Call the "real" save() method.

    @receiver(post_save, sender=User)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        logger.info("post_save signal.")
        if created:
            Token.objects.create(user=instance)
