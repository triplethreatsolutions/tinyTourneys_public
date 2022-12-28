# std imports
import logging

# Django imports
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseBadRequest

from django.views.decorators.clickjacking import xframe_options_exempt

# Imports from app
from settings.base import *
from .forms import ContactForm
from .models import Contact

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create your views here.


def contact_sent(request):
    return render(request, "contacts/contact-sent.html", {})


@xframe_options_exempt
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Unpack form values
            name = form.cleaned_data["name"]
            message = form.cleaned_data["message"]
            email = form.cleaned_data["email"]
            this_contact = Contact(name=name, message=message, email=email)
            this_contact.submit()
            # try:
            # create subject line
            subject = ("tinyTourneys Contact Form -" + name).replace("\n", "")
            # create body message
            msg = "Message: " + message + "\r\n\r\n Email: " + email

            try:
                email = EmailMessage(
                    subject=subject,
                    body=msg,
                    from_email=DEFAULT_FROM_EMAIL,
                    to=[
                        SERVER_EMAIL,
                    ],
                    reply_to=[email.replace("\n", "")],
                    headers={
                        "header": "none",
                    },
                )

                email.send(fail_silently=False)

            except Exception as e:
                logger.error(e)
                return HttpResponseBadRequest

            return HttpResponseRedirect("/contact-sent/")
    else:
        form = ContactForm()

    return render(request, "contacts/contact.html", {"form": form})
