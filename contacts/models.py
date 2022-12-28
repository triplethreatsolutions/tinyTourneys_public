from django.db import models
from django.utils import timezone

# Create your models here.


class Contact(models.Model):

    name = models.CharField("Name", max_length=30)
    message = models.TextField("Message")
    email = models.EmailField("Email", blank=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def submit(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return "%s" % self.name
