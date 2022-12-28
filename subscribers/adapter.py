# Std imports

# django imports
from django.contrib.auth.models import Permission

# 3rd party imports
from allauth.account.adapter import DefaultAccountAdapter

# app imports
from .permissions import *

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        user = context["user"]
        orgs = user.organization_admin.all()
        # Adding the activation code to the context for displaying in the email
        activation_code = "ERROR!"
        for org in orgs:
            activation_code = org.activationCode
        ctx = {
            "activation_code": activation_code,
        }
        context.update(ctx)
        super(CustomAccountAdapter, self).send_mail(template_prefix, email, context)

    def confirm_email(self, request, email_address):
        """
        Confirms activation code is valid before
        marking the email address as confirmed on the db
        """
        code = request.POST.get("activation_code")
        org = Organization.objects.get(admin__email=email_address)
        if org.activationCode == int(code):
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
        else:
            email_address.verified = False
            email_address.set_as_primary(conditional=False)
        email_address.save()

    def save_user(self, request, user, form, commit=False):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        # Do not persist the user yet so we pass commit=False
        # (last argument)
        admin = super(CustomAccountAdapter, self).save_user(
            request, user, form, commit=commit
        )
        # update user field with email address
        admin.username = admin.email
        admin.is_OrgAdmin = True
        # Create the User record
        admin.save()
        # set default permission for admins
        permission = Permission.objects.get(codename="can_view_organizations")
        admin.user_permissions.add(permission)
        permission = Permission.objects.get(codename="can_edit_organization")
        admin.user_permissions.add(permission)
        # Create the User record
        admin.save()

        # Create Organization Record
        name = form.cleaned_data["org_name"]
        primary_phone = form.cleaned_data["phone_number"]
        secondary_phone = ""
        address_one = ""
        address_two = ""
        city = ""
        state = ""
        zip_code = ""
        stripe_id = "none"
        org = Organization(
            name=name,
            admin=admin,
            accountType=Organization.NEW,
            activationCode=0,
            primaryPhone=primary_phone,
            secondaryPhone=secondary_phone,
            AddressLine1=address_one,
            AddressLine2=address_two,
            AddressCity=city,
            AddressState=state,
            AddressZIP=zip_code,
            stripeID=stripe_id,
        )
        # Must save instance first before saving many-to-many relationships
        org.save()
        org.directors.add(admin)
        # Save the many-to-many relationship
        org.save()

        return user
