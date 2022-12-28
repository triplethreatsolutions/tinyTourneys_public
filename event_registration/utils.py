# std imports
import logging

# django core
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

# app imports
from settings.base import DEFAULT_FROM_EMAIL, SERVER_EMAIL
from common.utils import translate_state_selection
from event_registration import models as registration_model
from subscribers import models as sub
from tournaments import models as tournament_model
from tournaments import utils as tournament_utils

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_billing_info_object(validated_data):
    """
    Purpose of this function is to create a billing info object from
    the validated user input data coming from the registration form
    """

    state = translate_state_selection(validated_data.get("state", ""))

    first_name = validated_data.get("fname", "")
    last_name = validated_data.get("lname", "")
    phone = validated_data.get("phone", "")

    billing_info = registration_model.BillingInfo.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=validated_data.get("email", ""),
        primary_phone=phone,
        secondary_phone="",
        address_line1=validated_data.get("address", ""),
        address_line2="",
        address_city=validated_data.get("city", ""),
        address_state=state,
        address_zip=validated_data.get("zip", ""),
    )

    return billing_info


def calculate_total_cost(quantity=0, cost=0, promo_value=0):
    """Calculate total cost and fees per line item"""
    # add in stripe fees to cover transaction cost
    single_cost = float(cost) - float(promo_value)

    # determine base cost before fees
    base_cost = single_cost * float(quantity)

    # Stripe fixed percent fee
    fixed_percent = 0.971
    fixed_fee = single_cost + 0.30
    # calculate base cost per line item
    stripe_cost = format(fixed_fee / fixed_percent, ".2f")
    # calculate processing fees per line item
    total_fee = float(stripe_cost) - float(single_cost)

    # factor in the quantity once we know cost per line item
    total_cost = float(stripe_cost) * float(quantity)
    total_fee = float(total_fee) * float(quantity)

    return (
        format(total_cost, ".2f"),
        stripe_cost,
        format(base_cost, ".2f"),
        format(total_fee, ".2f"),
        single_cost,
    )


def build_products_and_line_items(
    stripe, invoice, event, staff, cost, entry_cost, validated_data
):
    """
    Purpose of this function is to create an invoice line item for
    each team that was submitted during registration.

    The validated_data parameter contains the team name, division name
    and the dB division ID for easier processing.

    The cost parameter contains the entry fee plus Stripe processing fees

    The title parameter is the tournament title name

    The stripe parameter is passing in our secure instance of Stripe
    """
    details = str()
    line_items = list()

    # Get Organization by event ID
    organization = sub.Organization.objects.get(admin_id=event.director.id)

    for team in validated_data["teams"]:
        items = list(team.values())
        # Get division loaded by fixture
        division = tournament_model.Division.objects.get(pk=int(items[2]))
        # Get pools available for division, but only grab first available
        pool = tournament_model.Pool.objects.filter(division=division)[0]

        team = tournament_model.Team.objects.create(
            event=event,
            name=items[0],
            division=division,
            pool=pool,
            gender="NA",
            ageGroup="NA",
        )
        tournament_utils.add_staff_to_team(team, staff)

        registration = registration_model.Registration.objects.create(
            organization=organization,
            invoice=invoice,
            event=event,
            team=team,
            registrationStatus=registration_model.Registration.NEW,
            entryFee=entry_cost,
            comments=validated_data["comments"],
            disclaimer_accepted=False,
        )

        product = stripe.Product.create(
            name=str(items[0]),
            description=event.title + f" ~ ({items[1]})",
            statement_descriptor="tinyTourneys.com",
            metadata={
                "reg_id": str(registration.referenceID),
                "division": str(items[1]),
                "division_id": str(items[2]),
            },
            stripe_account=organization.stripeID,
        )

        # remove the decimal before creating Stripe Price object below
        cost = str(cost).replace(".", "")

        price = stripe.Price.create(
            unit_amount=cost,
            currency="usd",
            nickname=event.title,
            product=product,
            stripe_account=organization.stripeID,
        )

        item = {
            "price": price,
            "quantity": 1,  # This stays at 1, we figure out total based on quantity above
            "description": event.title + f" ~ ({items[1]})",
        }

        line_items.append(item)
        details += f"{items[0]} ({items[1]}), "

    return details, line_items


def email_receipt_to_customer(
    event, staff, invoice, comments, line_items, configuration
):
    # create subject line
    subject = (event.title + " Registration Receipt").replace("\n", "")
    # create body message
    msg = (
        "Purchase Order#: "
        + invoice.purchaseOrderID
        + "\r\n\r\n"
        + "Amount Paid: $"
        + str(invoice.amountDue)
        + "\r\n\r\n"
        + "Date Registered: "
        + timezone.now().strftime("%B %d, %Y")
        + "\r\n\r\n"
        + "Teams:\r\n"
        + line_items
        + "\r\n\r\n"
        + "Staff:"
        + "\r\n"
        + staff["fname"]
        + " "
        + staff["lname"]
        + " ("
        + staff["role"]
        + ")"
        + "\r\n"
        + staff["email"]
        + "\r\n"
        + staff["phone"]
        + "\r\n\r\n"
        + "Comments:"
        + "\r\n"
        + comments
        + "\r\n\r\n"
        + settings.DOMAIN_URL
        + "/event/"
        + event.slug
        + "\r\n\r\n"
        + "Look forward to seeing you at our event! Thank you!"
        + "\r\n"
        + event.director.get_full_name()
        + " (Event Director)"
        + "\r\n\r\n"
        + "Disclaimer:"
        + "\r\n"
        + configuration.disclaimer
    )
    # generate mailing list to notify registration was completed
    to_addresses = list()
    to_addresses.append(("Director", event.director.email.replace("\n", "")))
    to_addresses.append(
        (staff["fname"] + " " + staff["lname"], staff["email"].replace("\n", ""))
    )

    logger.info(str(to_addresses))
    logger.info(subject + "\r\n" + msg)

    try:
        email = EmailMessage(
            subject=subject,
            body=msg,
            from_email=DEFAULT_FROM_EMAIL,
            to=to_addresses,
            bcc=[
                SERVER_EMAIL,
            ],
            # reply_to=[staff.email.replace("\n", "")],
            headers={
                "header": "none",
            },
        )

        email.send(fail_silently=False)

        # remove all emails from list
        del to_addresses[:]

    except Exception as e:
        logger.error(e)
        return False

    return True
