from django import forms
from django.core.validators import RegexValidator

# 3rd Part Packages
from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

# app imports
from .models import *

User = get_user_model()


class SubscriberFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SubscriberFormHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.form_show_errors = True
        self.label_class = "yellow"
        self.form_class = "form-inline"
        # self.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout = Layout(
            Fieldset("", "org_name", "first_name", "last_name", "phone_number"),
            Fieldset("", "email", "password1", "password2"),
        )
        self.add_input(
            Submit("submit", "Create Free Account", css_class="btn-default btn-lg")
        )
        self.render_required_fields = True


class SubscriberForm(SignupForm):
    org_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Organization"}
        ),
    )

    first_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    phone_number = forms.CharField(
        label="Phone Number",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        ),
        error_messages={"incomplete": "Enter a phone number."},
        validators=[RegexValidator(r"^[0-9]+$", "Enter a valid phone number.")],
    )

    def __init__(self, *args, **kwargs):
        super(SubscriberForm, self).__init__(*args, **kwargs)
        self.helper = SubscriberFormHelper

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(SubscriberForm, self).save(request)

        # Add your own processing here.

        # You must return the original result.
        return user
