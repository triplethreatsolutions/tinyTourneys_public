# Core imports
from django.shortcuts import reverse
from django.views.generic import TemplateView

# 3rd Party imports
from allauth.account.views import ConfirmEmailView


class SchemaUIView(TemplateView):

    template_name = "api/schema_view.html"

    def get_context_data(self, **kwargs):
        context = super(SchemaUIView, self).get_context_data(**kwargs)
        context["schema_url"] = "api:openapi-schema"
        return context
