from django.conf.urls import url
from . import views

app_name = "contacts"

urlpatterns = [
    # function based view (FBV)
    url(r"^contact/$", views.contact, name="contact"),
    # function based view (FBV)
    url(r"^contact-sent/$", views.contact_sent, name="contact-sent"),
]
