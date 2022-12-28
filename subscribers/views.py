# std imports
from django.shortcuts import render
from django.views import generic

# 3rd party imports
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

# app imports
from .serializer import *
from .permissions import *
from subscribers import models
from common.utils import email_admin

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)

User = get_user_model()


class InterestedEmailView(generic.View):
    def post(self, request):
        context = {}
        if self.request.method == "POST" and "email" in self.request.POST:
            email = self.request.POST.get("email")
            if email:
                interested = models.InterestedEmail(email=email)
                interested.save()
                logger.info(f"{email} was interested at {interested.created}")
                email_admin(subject="Interested Email", session_data=self.request.POST)
                context["message"] = "Awesome! We got it. We'll be in touch soon!"
                return render(
                    request, "subscribers/interested_confirmation.html", context=context
                )
            else:
                context["message"] = "Sorry...we didn't see anything. Please try again!"
                return render(
                    request, "subscribers/interested_confirmation.html", context=context
                )


class ListOrganizations(generics.ListCreateAPIView):
    """
    Returns a list of all **active** organizations in the system.

    For more details on how accounts are activated please [see here][ref].

    [ref]: www.tinyTourneys.com
    """

    serializer_class = OrganizationSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        objs = Organization.objects.filter(admin_id=self.request.user.id)
        return objs


class DetailOrganization(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "referenceID"
    lookup_url_kwarg = "referenceID"
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, CanEditOrg]

    def get_queryset(self):
        obj = Organization.objects.filter(referenceID=self.kwargs.get("referenceID"))
        return obj
