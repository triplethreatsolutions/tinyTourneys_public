# std imports
import logging
import json

# django imports
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse

# 3rd party imports
from rest_framework import generics
from rest_framework import permissions
from rest_framework.parsers import JSONParser
import stripe

# app imports
from common.utils import email_admin
from event_registration import models as registration_model
from event_registration import serializers
from event_registration import utils
from subscribers.models import Organization
from tournaments import models as tournament_model
from tournaments import utils as tournament_utils

# Create a custom logger
from users.models import CustomUser

logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create your views here.


class RegistrationSuccessView(TemplateView):
    template_name = "event_registration/success.html"


class RegistrationCancelView(TemplateView):
    template_name = "event_registration/cancel.html"


def cancel_checkout_session(request):
    if request.method == "GET":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET.get("session_id")
        event_slug = request.GET.get("event")

        # collect event and organization details
        try:
            event = tournament_model.Event.objects.get(slug=event_slug)
            user = CustomUser.objects.get(username=event.director)
            org = Organization.objects.get(admin=user)
        except ObjectDoesNotExist as e:
            logger.error(
                "Event or director do not exist for this registration: {}".format(
                    str(e)
                )
            )
            return render(request, "http_response/404.html", status=404)

        checkout_session = stripe.checkout.Session.retrieve(
            session_id, stripe_account=org.stripeID
        )
        line_items = stripe.checkout.Session.list_line_items(
            checkout_session["id"], stripe_account=org.stripeID
        )
        invoice = registration_model.Invoice.objects.get(
            purchaseOrderID=checkout_session["metadata"]["invoice_po"]
        )

        # walk thru each registration, delete team and registration as we go
        for item in line_items:
            product = stripe.Product.retrieve(
                item.price.product, stripe_account=org.stripeID
            )
            registration = registration_model.Registration.objects.get(
                referenceID=product.metadata.reg_id
            )
            registration.team.delete()
            registration.delete()

        # Due to relationships, delete invoice last
        invoice.delete()

        return JsonResponse({"status": "registration session has been cancelled"})


def get_checkout_session(request):
    if request.method == "GET":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET.get("session_id")
        event_slug = request.GET.get("event")

        # collect event and organization details
        try:
            event = tournament_model.Event.objects.get(slug=event_slug)
            user = CustomUser.objects.get(username=event.director)
            org = Organization.objects.get(admin=user)
        except ObjectDoesNotExist as e:
            logger.error(
                "Event or director do not exist for this registration: {}".format(
                    str(e)
                )
            )
            return render(request, "http_response/404.html", status=404)

        checkout_session = stripe.checkout.Session.retrieve(
            session_id, stripe_account=org.stripeID
        )
        event = tournament_model.Event.objects.get(
            slug=checkout_session["metadata"]["event_slug"]
        )
        configuration = registration_model.Configuration.objects.get(event=event)
        invoice = registration_model.Invoice.objects.get(
            purchaseOrderID=checkout_session["metadata"]["invoice_po"]
        )
        registrations = registration_model.Registration.objects.filter(
            invoice__purchaseOrderID=checkout_session["metadata"]["invoice_po"]
        ).select_related("team")

        staff = dict()
        staff["email"] = checkout_session["metadata"]["email"]
        staff["role"] = checkout_session["metadata"]["role"]
        staff["fname"] = checkout_session["metadata"]["fname"]
        staff["lname"] = checkout_session["metadata"]["lname"]
        staff["phone"] = checkout_session["metadata"]["phone"]

        teams = list()
        line_items = ""
        comments = ""
        for reg in registrations:
            item = {
                "entry_fee": reg.entryFee,
                "name": reg.team.name,
                "division": reg.team.division.name,
            }
            line_items += f"{reg.team.name} ({reg.team.division.name} Division)\r\n"
            comments = reg.comments
            teams.append(item)
        utils.email_receipt_to_customer(
            event, staff, invoice, comments, line_items, configuration
        )
        return JsonResponse(
            {
                "event_title": event.title,
                "teams": teams,
                "invoice_fees": invoice.processingFee,
                "session_id": checkout_session,
            }
        )


def get_registration_fees(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        promo_code = data["promocode"]
        event_slug = data["event_slug"]
        quantity = data["quantity"]

        try:
            # Get event loaded by fixture
            event = tournament_model.Event.objects.get(slug=event_slug)
            # Get configuration details
            configuration = registration_model.Configuration.objects.get(pk=event.id)
            if configuration.promoEnabled and configuration.promoCode == promo_code:
                promo_value = configuration.promoValue
            else:
                promo_value = 0

            (
                total_cost,
                stripe_cost,
                base_cost,
                processing_fee,
                single_cost,
            ) = utils.calculate_total_cost(
                quantity=quantity, cost=configuration.entryFee, promo_value=promo_value
            )
            discount = promo_value * quantity

            return JsonResponse(
                {
                    "cost": str(base_cost),
                    "fees": str(processing_fee),
                    "total_cost": str(total_cost),
                    "discount": format(discount, ".2f"),
                }
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({"failed_request": str(e)})

    return JsonResponse({"failed_request": "not a post request"})


# Webhooks are always sent as HTTP POST requests, so ensure
# that only POST requests reach your webhook view by
# decorating `webhook()` with `require_POST`.
#
# To ensure that the webhook view can receive webhooks,
# also decorate `webhook()` with `csrf_exempt`.
@require_POST
@csrf_exempt
def checkout_session_webhook(request):
    logger.info("Checkout session webhook...")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        logger.error(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(e)
        return HttpResponse(status=400)

        # Handle the event
    if event.type == "checkout.session.completed":
        logger.info(event.type)
        session = event.data.object  # contains a stripe.Checkoutsession
        # collect event and organization details
        try:
            event = tournament_model.Event.objects.get(
                slug=session["metadata"]["event_slug"]
            )
            user = CustomUser.objects.get(username=event.director)
            org = Organization.objects.get(admin=user)
        except ObjectDoesNotExist as e:
            logger.error(
                "Event or director do not exist for this registration: {}".format(
                    str(e)
                )
            )
            email_admin(subject="Error Creating Team", session_data=session)
            return render(request, "http_response/404.html", status=404)

        line_items = stripe.checkout.Session.list_line_items(
            session["id"], stripe_account=org.stripeID
        )
        status = finalize_team_registration(session["metadata"], line_items, org)
        if not status:
            email_admin(subject="Error Creating Team", session_data=session)
            return HttpResponse(status=403)
    else:
        logger.info(event.type)
    return HttpResponse(status=200)


@require_POST
@csrf_exempt
def checkout_session_webhook_connect(request):
    logger.info("Checkout session webhook connected account...")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_CONNECTED_KEY

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        logger.error(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(e)
        return HttpResponse(status=400)

    # Handle the event
    logger.info(event.type)
    logger.info(event.data)
    return HttpResponse(status=200)


def create_checkout_session(request):
    if request.method == "POST":
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Parse request data into Python native datatype...
            data = JSONParser().parse(request)

            quantity = data["quantity"]

            # Double check that the quantity is not zero before continuing
            if int(quantity) == 0:
                raise Exception

            # Add null invoice purchase order so we can serialize the remaining data
            data["data"]["invoice_po"] = "TTnull"

            # then we restore those native datatype into a fully populated object instance
            serializer = serializers.TeamRegistrationSerializer(data=data["data"])
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden(str(e))

        valid = False
        if serializer.is_valid():
            valid = True
        else:
            str_data = json.dumps(data)
            logger.error(str(serializer.errors) + " - %s", str_data)
            return HttpResponseForbidden()

        try:
            if valid:

                try:
                    # collect event and registration configuration details
                    event = tournament_model.Event.objects.get(
                        slug=serializer.validated_data["event_slug"]
                    )
                    try:
                        user = CustomUser.objects.get(username=event.director)
                        org = Organization.objects.get(admin=user)
                    except ObjectDoesNotExist as e:
                        logger.error(
                            "Event director does not exist for this registration: {}".format(
                                str(e)
                            )
                        )
                        return render(request, "http_response/404.html", status=404)

                    config = registration_model.Configuration.objects.get(pk=event.id)
                    # validate a promo code was entered and matches
                    if (
                        config.promoEnabled
                        and config.promoCode == serializer.validated_data["promocode"]
                    ):
                        promo_value = config.promoValue
                    else:
                        promo_value = 0
                except Exception as e:
                    logger.error(e)
                    return HttpResponseForbidden(str(e))

                # Create new Checkout Session for the order
                # Other optional params include:
                # [billing_address_collection] - to display billing address details on the page
                # [customer] - if you have an existing Stripe Customer ID
                # [payment_intent_data] - lets capture the payment later
                # [customer_email] - lets you prefill the email input in the form
                # For full details see https:#stripe.com/docs/api/checkout/sessions/create
                # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param

                customer = stripe.Customer.create(
                    name=serializer.validated_data["fname"]
                    + " "
                    + serializer.validated_data["lname"],
                    email=serializer.validated_data["email"],
                    phone=serializer.validated_data["phone"],
                    address={
                        "city": serializer.validated_data["city"],
                        "line1": serializer.validated_data["address"],
                        "state": serializer.validated_data["state"],
                        "postal_code": serializer.validated_data["zip"],
                    },
                    description=event.title,
                    stripe_account=org.stripeID,
                )

                (
                    final_cost,
                    stripe_cost,
                    base_cost,
                    processing_fee,
                    single_cost,
                ) = utils.calculate_total_cost(
                    quantity=quantity, cost=config.entryFee, promo_value=promo_value
                )

                # Create the staff object for this registration event
                staff = tournament_utils.create_staff_object(serializer.validated_data)
                # Create the billing info object for the invoice
                billing_info = utils.create_billing_info_object(
                    serializer.validated_data
                )

                invoice = registration_model.Invoice.objects.create(
                    invoiceStatus=registration_model.Invoice.DRAFT,
                    billingInfo=billing_info,
                    amountDue=final_cost,
                    amountPaid=0,
                    processingFee=processing_fee,
                    taxes=0,
                    paymentMethod=100,
                )  # 100 == Credit Card

                details, line_items = utils.build_products_and_line_items(
                    stripe,
                    invoice,
                    event,
                    staff,
                    stripe_cost,
                    single_cost,
                    serializer.validated_data,
                )

                # add invoice purchase order to checkout session meta data
                serializer.validated_data["invoice_po"] = invoice.purchaseOrderID
                logger.info(
                    "Checkout Session Data: %s", json.dumps(serializer.validated_data)
                )
                # Stripe checkout does not handle a nested dictionary, clear out items
                serializer.validated_data["teams"].clear()

                checkout_session = stripe.checkout.Session.create(
                    customer=customer,
                    payment_method_types=["card"],
                    line_items=line_items,
                    metadata=serializer.validated_data,
                    mode="payment",
                    success_url=settings.DOMAIN_URL
                    + reverse("event_registration:registration_success")
                    + "?session_id={CHECKOUT_SESSION_ID}&event="
                    + str(event.slug),
                    cancel_url=settings.DOMAIN_URL
                    + reverse("event_registration:registration_cancel")
                    + "?session_id={CHECKOUT_SESSION_ID}&event="
                    + str(event.slug),
                    stripe_account=org.stripeID,
                )

                stripe.PaymentIntent.modify(
                    checkout_session["payment_intent"],
                    description=event.title + " ~ " + details,
                    stripe_account=org.stripeID,
                )
            else:
                raise TypeError("%s".format(serializer.errors))
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden(str(e))


def finalize_team_registration(data, line_items, org):
    try:
        # store data into a fully populated object instance
        serializer = serializers.RegistrationMetaSerializer(data=data)

        if serializer.is_valid():
            # Get the invoice record
            invoice = registration_model.Invoice.objects.get(
                purchaseOrderID=serializer.validated_data["invoice_po"]
            )
            # If invoice has been paid, then registration was already completed
            if invoice.invoiceStatus != registration_model.Invoice.PAID:
                # Pull out line items team for registration.
                for item in line_items:
                    product = stripe.Product.retrieve(
                        item.price.product, stripe_account=org.stripeID
                    )
                    registration = registration_model.Registration.objects.get(
                        referenceID=product.metadata.reg_id
                    )
                    registration.registrationStatus = (
                        registration_model.Registration.COMPLETED
                    )
                    registration.disclaimer_accepted = True
                    registration.save()
                    # # Get division loaded by fixture
                    division = tournament_model.Division.objects.get(
                        pk=int(product.metadata.division_id)
                    )
                    # update time stamp on division after adding team
                    division.publish()

                # checkout session was completed, update invoice parameters
                invoice.invoiceStatus = registration_model.Invoice.PAID
                invoice.amountPaid = invoice.amountDue
                invoice.save()
                logger.info("Team registration successful. {}".format(invoice))
            else:
                logger.info(
                    "Team registration already completed, tried again for some reason."
                )
                logger.info("%s", json.dumps(serializer.validated_data))
            return True
        else:
            # Something didn't go right validating the metadata
            logger.error(str(serializer.errors) + " - %s", json.dumps(data))
            return False

    except Exception as e:
        logger.error(e)
        return False


def registration_register_view(request, slug):
    if request.method == "GET":
        data = dict()
        divs = list()

        # Make sure the event exists before setting up view
        try:
            event = tournament_model.Event.objects.get(slug=slug)
        except ObjectDoesNotExist:
            logger.info("Event Does Not Exist: " + str(request.path))
            return render(request, "http_response/403.html", status=403)

        user = CustomUser.objects.get(username=event.director)
        org = Organization.objects.get(admin=user)

        try:
            configuration = registration_model.Configuration.objects.get(pk=event.id)
        except ObjectDoesNotExist as e:
            logger.error(
                "Event is not configured for registration yet: {}".format(str(e))
            )
            return render(
                request, "http_response/404.html", status=404, context={"user": user}
            )

        divisions = tournament_model.Division.objects.filter(event__slug=slug)
        data["title"] = event.title
        data["startDate"] = event.start_date.strftime("%B %d, %Y")
        data["endDate"] = event.end_date.strftime("%B %d, %Y")
        data["description"] = event.description
        data["information"] = configuration.info
        data["entryFee"] = configuration.entryFee
        data["registrationState"] = configuration.registrationState
        data["disclaimerEnabled"] = configuration.disclaimerEnabled
        data["disclaimer"] = configuration.disclaimer
        data["promoEnabled"] = configuration.promoEnabled
        data["eventSlug"] = slug
        data["connected_account"] = org.stripeID
        for div in divisions:
            data[div.name] = div.id
            divs.append(div.name)
        data["divisions"] = divs
        return render(
            request, "event_registration/register.html", {"event": event, "data": data}
        )
    else:
        return render(request, "http_response/403.html", status=403)


class ListTeams(generics.ListCreateAPIView):
    queryset = (
        tournament_model.Team.objects.all()
        .select_related("head_coach")
        .select_related("assistant_coach")
        .select_related("team_director")
    )
    serializer_class = serializers.TeamSerializer
    permission_classes = [
        permissions.AllowAny,
    ]


class DetailTeam(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    serializer_class = serializers.TeamSerializer

    def get_queryset(self):
        obj = tournament_model.Team.objects.filter(pk=self.kwargs.get("pk"))
        return obj


class ListRegistrations(generics.ListCreateAPIView):
    queryset = registration_model.Registration.objects.all()
    serializer_class = serializers.RegistrationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]


class DetailRegistration(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "referenceID"
    lookup_url_kwarg = "referenceID"
    serializer_class = serializers.RegistrationSerializer

    def get_queryset(self):
        obj = registration_model.Registration.objects.filter(
            referenceID=self.kwargs.get("referenceID")
        )
        return obj


class ListInvoices(generics.ListCreateAPIView):
    queryset = registration_model.Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]


class DetailInvoice(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "referenceID"
    lookup_url_kwarg = "referenceID"
    serializer_class = serializers.InvoiceSerializer

    def get_queryset(self):
        obj = registration_model.Invoice.objects.filter(
            referenceID=self.kwargs.get("referenceID")
        )
        return obj


class ListConfigurations(generics.ListCreateAPIView):
    queryset = registration_model.Configuration.objects.all()
    serializer_class = serializers.ConfigurationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]


class DetailConfiguration(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ConfigurationSerializer
    permission_classes = [
        permissions.AllowAny,
    ]

    def get_queryset(self):
        obj = registration_model.Configuration.objects.filter(pk=self.kwargs.get("pk"))
        return obj


class ListQuestions(generics.ListCreateAPIView):
    queryset = registration_model.Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    permission_classes = [
        permissions.AllowAny,
    ]


class DetailQuestion(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.QuestionSerializer

    def get_queryset(self):
        obj = registration_model.Question.objects.filter(pk=self.kwargs.get("pk"))
        return obj


class ListAnswers(generics.ListCreateAPIView):
    queryset = registration_model.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer
    permission_classes = [
        permissions.AllowAny,
    ]


class DetailAnswer(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.AnswerSerializer

    def get_queryset(self):
        obj = registration_model.Answer.objects.filter(pk=self.kwargs.get("pk"))
        return obj
