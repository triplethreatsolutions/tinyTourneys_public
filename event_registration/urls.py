from django.urls import path
from common.views import *
from .views import *

# Namespacing URL names # i.e. url 'event_registration:registration_new'
app_name = "event_registration"

urlpatterns = [
    # function based view (FBV)
    path("config/", get_publishable_key, name="registration_config"),
    path(
        "create-checkout-session",
        create_checkout_session,
        name="registration_create_session",
    ),
    path(
        "checkout-session/", get_checkout_session, name="registration_checkout_session"
    ),
    path(
        "checkout-session-webhook/",
        checkout_session_webhook,
        name="registration_checkout_session_webhook",
    ),
    path(
        "checkout-session-webhook/connect/",
        checkout_session_webhook_connect,
        name="registration_checkout_session_webhook_connect",
    ),
    # function based view (FBV)
    path("<slug:slug>", registration_register_view, name="registration_register"),
    path("registration-fees/", get_registration_fees, name="registration_fees"),
    path("success/", RegistrationSuccessView.as_view(), name="registration_success"),
    path("cancel/", RegistrationCancelView.as_view(), name="registration_cancel"),
    path(
        "cancel-checkout/", cancel_checkout_session, name="registration_cancel_checkout"
    ),
]
