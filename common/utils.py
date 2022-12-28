# std imports
import string
import random
from datetime import datetime
import logging
import json

# Create a custom logger
from django.core.mail import EmailMessage
from django.urls import reverse

from settings.base import DEFAULT_FROM_EMAIL, ADMINS
from common.constants import STATES

logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def unique_id_gen():
    (dt, micro) = datetime.utcnow().strftime("%Y%m%d.%f").split(".")
    dt = "%s%03d" % (dt, int(micro) / 1000)
    return "".join(
        [
            "TT",
            dt,
            "".join(random.sample(string.ascii_uppercase, 3)),
            "".join(random.sample(string.digits, 3)),
        ]
    )


def unique_hash_gen():
    (dt, micro) = datetime.utcnow().strftime("%Y%m%d%H%M%S.%f").split(".")
    dt = "%s" % dt
    # print(''.join([dt, ]))
    return "".join(
        [
            dt,
        ]
    )


def activation_code_gen():
    micro = datetime.utcnow().strftime("%f")
    # make sure its always 6 digits in length
    while len(micro) < 6:
        logger.info(
            "activation_code_gen() is less than six digits, trying again: %d"
            % (int(micro))
        )
        micro = datetime.utcnow().strftime("%f")
    return int(micro)


# Convert full State name to its abbreviation
def translate_state_selection(data):
    if not data:
        return "NA"
    for abbrev, full_name in STATES:
        if data == full_name:
            return abbrev


def email_admin(subject, session_data):
    # create body message
    msg = "Data: " + "\r\n\r\n" + json.dumps(session_data, sort_keys=True, indent=4)

    try:
        email = EmailMessage(
            subject=subject,
            body=msg,
            from_email=DEFAULT_FROM_EMAIL,
            to=ADMINS,
            headers={
                "header": "none",
            },
        )

        email.send(fail_silently=False)

    except Exception as e:
        logger.error(e)


def generate_account_link(account_id, origin, stripe):
    account_link = stripe.AccountLink.create(
        type="account_onboarding",
        account=account_id,
        refresh_url=f"{origin}" + reverse("tournaments:stripe_onboard_refresh"),
        return_url=f"{origin}" + reverse("tournaments:stripe_onboard_return"),
    )
    return account_link.url
