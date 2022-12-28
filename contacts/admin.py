from django.contrib import admin
from tournaments.admin import tourney_admin_site
from .models import Contact

# Register your models here.


@admin.register(Contact, site=tourney_admin_site)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "published_date",
        "name",
        "email",
        "message",
    )
