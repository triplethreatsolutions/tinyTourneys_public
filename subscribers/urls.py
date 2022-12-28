from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from subscribers import views

# Namespacing URL names # i.e. url 'tournaments:event_list'
app_name = "subscribers"

urlpatterns = [
    # Authentication URLs for standard django auth - replaced by django all-auth views
    path(
        "login/",
        LoginView.as_view(template_name="subscribers/login.html"),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(template_name="subscribers/login.html"),
        name="logout",
    ),
    path("interested/", views.InterestedEmailView.as_view(), name="interested_email"),
]
