# api/urls.py
# Core imports
from django.conf.urls import url, include
from django.urls import path


# 3rd Party imports
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view

# App imports
from .views import *
from event_registration.views import *
from tournaments import api
from subscribers.views import *

app_name = "api"

API_TITLE = "tinyTourneys APIs"
API_VERSION = 1.0
API_DESCRIPTION = "A web API schema for managing our dashboard and event registration"


schema_view = get_schema_view(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    urlconf="api.urls",
)


urlpatterns = [
    url("^rest-auth/", include("rest_auth.urls")),
    url("^rest-auth/registration/", include("rest_auth.registration.urls")),
    url("^organizations/$", ListOrganizations.as_view(), name="list_organizations"),
    url(
        "^organization/(?P<referenceID>[0-9A-Z_]{15})/$",
        DetailOrganization.as_view(),
        name="detail_organization",
    ),
    url("^teams/$", ListTeams.as_view(), name="list_teams"),
    path("team/<uuid:pk>", DetailTeam.as_view(), name="detail_team"),
    url("^staff/$", api.ListStaff.as_view(), name="list_staff"),
    path("staff/<uuid:pk>", api.DetailStaff.as_view(), name="detail_staff"),
    url("^registrations/$", ListRegistrations.as_view(), name="list_registrations"),
    url(
        "^registration/(?P<referenceID>[0-9A-Z_]{15})/$",
        DetailRegistration.as_view(),
        name="detail_registration",
    ),
    url("^invoices/$", ListInvoices.as_view(), name="list_invoices"),
    url(
        "^invoice/(?P<referenceID>[0-9A-Z_]{15})/$",
        DetailInvoice.as_view(),
        name="detail_invoice",
    ),
    url("^configurations/$", ListConfigurations.as_view(), name="list_configurations"),
    path(
        "configuration/<int:pk>",
        DetailConfiguration.as_view(),
        name="detail_configuration",
    ),
    url("^questions/$", ListQuestions.as_view(), name="list_questions"),
    path("question/<int:pk>", DetailQuestion.as_view(), name="detail_question"),
    url("^answers/$", ListAnswers.as_view(), name="list_answers"),
    path("answer/<int:pk>", DetailAnswer.as_view(), name="detail_answer"),
    url(r"^schema/$", schema_view, name="openapi-schema"),
    url(r"^docs/$", SchemaUIView.as_view(), name="schema-ui"),
]
