# Register your models here.

from tournaments.admin import tourney_admin_site
from .models import *

# Register your models here.
tourney_admin_site.register(Organization)
tourney_admin_site.register(InterestedEmail)
