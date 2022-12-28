# settings/production.py
from .base import *

DEBUG = False

# All-Auth
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

DOMAIN_URL = ACCOUNT_DEFAULT_HTTP_PROTOCOL + "://www.tinyTourneys.com"

STRIPE_PUBLISHABLE_KEY = get_env_variable("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = get_env_variable("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_KEY = get_env_variable("STRIPE_WEBHOOK_KEY")
STRIPE_WEBHOOK_CONNECTED_KEY = get_env_variable("STRIPE_WEBHOOK_CONNECTED_KEY")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# Each time a Web browser sees the HSTS header from your site,
# it will refuse to communicate non-securely (using HTTP) with
# your domain for the given period of time below (in seconds).
SECURE_HSTS_SECONDS = (
    0  # TODO: Change this to a non-zero value once ready for production use
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# The lifetime of a database connection, in seconds.
CONN_MAX_AGE = 300

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
