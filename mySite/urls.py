"""mySite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from tournaments.admin import tourney_admin_site


urlpatterns = [
    # url(r'^email-verification/$',
    #     TemplateView.as_view(template_name="email_verification.html"),
    #     name='email-verification'),
    # url(r'^password-reset/$',
    #     TemplateView.as_view(template_name="password_reset.html"),
    #     name='password-reset'),
    # url(r'^password-reset/confirm/$',
    #     TemplateView.as_view(template_name="password_reset_confirm.html"),
    #     name='password-reset-confirm'),
    #
    # url(r'^user-details/$',
    #     TemplateView.as_view(template_name="user_details.html"),
    #     name='user-details'),
    # url(r'^password-change/$',
    #     TemplateView.as_view(template_name="password_change.html"),
    #     name='password-change'),
    #
    # # this url is used to generate email content
    # url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     TemplateView.as_view(template_name="password_reset_confirm.html"),
    #     name='password_reset_confirm'),
    path("admin/", admin.site.urls),
    path("ttadmin/", tourney_admin_site.urls),
    # Standard Django auth
    # path('accounts/', include('django.contrib.auth.urls')),
    # All-Auth
    path("accounts/", include("allauth.urls")),
    path("api/v1/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("tournaments.urls")),
    path("registration/", include("event_registration.urls")),
    path("", include("subscribers.urls")),
    path("", include("contacts.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
