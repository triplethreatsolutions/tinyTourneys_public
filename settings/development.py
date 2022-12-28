# settings/development.py
from .base import *

DEBUG = True

# All-Auth
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

DOMAIN_URL = ACCOUNT_DEFAULT_HTTP_PROTOCOL + "://127.0.0.1:8000"

STRIPE_PUBLISHABLE_KEY = get_env_variable("STRIPE_TEST_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = get_env_variable("STRIPE_TEST_SECRET_KEY")
STRIPE_WEBHOOK_KEY = get_env_variable("STRIPE_TEST_WEBHOOK_KEY")
STRIPE_WEBHOOK_CONNECTED_KEY = get_env_variable("STRIPE_WEBHOOK_CONNECTED_KEY")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# The lifetime of a database connection, in seconds.
CONN_MAX_AGE = 300

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "staging-db.sqlite3"),
    }
}

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]
