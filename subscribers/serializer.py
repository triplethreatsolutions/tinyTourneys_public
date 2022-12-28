import logging

# django imports
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

# 3rd party imports
from rest_framework import serializers
from hashid_field.rest import HashidSerializerCharField

# app imports
from common.utils import unique_hash_gen, activation_code_gen
from .models import Organization

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "email",
            "is_staff",
            "is_active",
            "is_OrgAdmin",
            "date_joined",
        )


class OrganizationSerializer(serializers.ModelSerializer):
    referenceID = HashidSerializerCharField(
        source_field="subscribers.Organization.referenceID", read_only=True
    )
    admin = UserSerializer(many=False, required=False)
    directors = UserSerializer(many=True, required=False)

    class Meta:
        model = Organization
        fields = "__all__"

    def create(self, validated_data):
        # DRF does not support create method for nested serializers.
        # So we implement our own to handle M2M relationships
        admin = User.objects.create_user(
            username=validated_data["admin"].pop("username"),
            email=validated_data["admin"].pop("email"),
            password=validated_data["admin"].pop("password"),
            **validated_data["admin"]
        )
        # Since admin is foreign key, need to update
        # with the returned CustomUser object created above
        validated_data["admin"] = admin
        instance = Organization.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        # Find out if the admin user data exists, if not, create account
        found = User.objects.filter(
            username=validated_data["admin"].get("username")
        ).exists()
        if not found:
            admin = User.objects.create_user(
                username=validated_data["admin"].pop("username"),
                email=validated_data["admin"].pop("email"),
                password=validated_data["admin"].pop("password"),
                is_OrgAdmin=True,
                **validated_data["admin"]
            )
            permission = Permission.objects.get(codename="can_view_organizations")
            admin.user_permissions.add(permission)
            permission = Permission.objects.get(codename="can_edit_organization")
            admin.user_permissions.add(permission)
            admin.save()
            # Assign the returned CustomUser object back
            validated_data["admin"] = admin

        # Update instance with new data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        # Show related fields in an extended layout and not only with PKs
        representation = super(OrganizationSerializer, self).to_representation(instance)
        return representation
