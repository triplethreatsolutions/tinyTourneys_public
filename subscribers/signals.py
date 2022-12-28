# std imports
import logging

# django imports
from django.dispatch import receiver

# 3rd party imports
from allauth.account.signals import user_logged_in, email_confirmed

# app imports
from common.utils import email_admin
from subscribers.models import Organization
from users.models import CustomUser

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@receiver(user_logged_in)
def login_detected(sender, request, user, **kwargs):
    org = Organization.objects.get(admin=user)
    msg = {
        "Event": f"{login_detected.__name__}",
        "Org": f"{org.name}",
        "Email": f"{user.email}",
    }
    email_admin(f"{org.name} has logged in.", msg)
    logger.info(msg)


@receiver(email_confirmed)
def subscriber_signup(sender, request, email_address, **kwargs):
    user = CustomUser.objects.get(email=email_address)
    org = Organization.objects.get(admin=user)
    msg = {
        "Event": f"{subscriber_signup.__name__}",
        "Org": f"{org.name}",
        "Email": f"{user.email}",
        "Name": user.get_full_name(),
        "Phone": f"{org.primaryPhone}",
    }
    email_admin(f"{org.name} has signed up!", msg)
    logger.info(msg)
