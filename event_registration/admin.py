# Core Django imports
from django.contrib import admin

# Import for app
from tournaments.admin import tourney_admin_site
from .models import *


# Register your models here.
@admin.register(Registration, site=tourney_admin_site)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "referenceID",
        "invoice",
        "event",
        "team",
        "registrationStatus",
        "created",
    )
    list_select_related = (
        "event",
        "team",
        "invoice",
    )
    ordering = ["-created"]
    list_filter = ("event",)


# Register your models here.
@admin.register(Invoice, site=tourney_admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "purchaseOrderID",
        "referenceID",
        "invoiceStatus",
        "amountDue",
        "amountPaid",
        "created",
    )
    ordering = ["-created"]


tourney_admin_site.register(BillingInfo)
tourney_admin_site.register(Question)
tourney_admin_site.register(Answer)
tourney_admin_site.register(Configuration)
