import logging

# 3rd party imports
from rest_framework import serializers
from hashid_field.rest import HashidSerializerCharField

# app imports
from event_registration.models import (
    Registration,
    Invoice,
    Configuration,
    Question,
    Answer,
)
from tournaments import models as tournament_model

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TeamDivisionSerializer(serializers.Serializer):
    """This serializer handles the minimum required data for teams registering"""

    name = serializers.CharField(max_length=100)
    division = serializers.CharField(max_length=100)
    division_id = serializers.IntegerField()


class TeamRegistrationSerializer(serializers.Serializer):
    """This serializer handles the main user data coming in from a registration instance"""

    invoice_po = serializers.CharField(max_length=100)
    event_slug = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=100)
    fname = serializers.CharField(max_length=200)
    lname = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=200)
    state = serializers.CharField(max_length=50)
    zip = serializers.CharField(max_length=5)
    comments = serializers.CharField(max_length=200)
    promocode = serializers.CharField(max_length=25)
    teams = TeamDivisionSerializer(many=True)


class RegistrationMetaSerializer(serializers.Serializer):
    """This serializer handles the meta data coming back from Stripe"""

    invoice_po = serializers.CharField(max_length=100)
    event_slug = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    role = serializers.CharField(max_length=100)
    fname = serializers.CharField(max_length=200)
    lname = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=200)
    state = serializers.CharField(max_length=50)
    zip = serializers.CharField(max_length=5)
    comments = serializers.CharField(max_length=200)
    promocode = serializers.CharField(max_length=25)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = tournament_model.Team
        fields = "__all__"

    def create(self, validated_data):
        # DRF does not support create method for nested serializers.
        # So we implement our own to handle M2M relationships

        # Save the Team object once we've popped the M2M objects off
        instance = tournament_model.Team.objects.create(**validated_data)
        # Once we've finished creating and adding the M2M objects, save
        instance.save()
        return instance

    def update(self, instance, validated_data):
        rows = tournament_model.Team.objects.update(**validated_data)
        return tournament_model.Team.objects.get(pk=instance.pk)

    def to_representation(self, instance):
        # Show related fields in an extended layout and not only with PKs
        representation = super(TeamSerializer, self).to_representation(instance)
        return representation


class InvoiceSerializer(serializers.ModelSerializer):
    referenceID = HashidSerializerCharField(
        source_field="event_registration.Invoice.referenceID", read_only=True
    )

    class Meta:
        model = Invoice
        fields = "__all__"


class RegistrationSerializer(serializers.ModelSerializer):
    referenceID = HashidSerializerCharField(
        source_field="event_registration.Registration.referenceID", read_only=True
    )

    class Meta:
        model = Registration
        fields = "__all__"


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"
