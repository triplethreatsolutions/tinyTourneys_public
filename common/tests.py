# std imports
import logging

# django imports
from django.core.management import call_command
from django.test import TestCase
from django.apps import apps

# Collecting project code metrics here.

# Create a custom logger
logging.basicConfig(format="%(name)s - %(funcName)s: ", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseTests(TestCase):
    def test_missing_migrations(self):
        """
        If no migrations are detected as needed, 'result' will be 'None'.
        In all other cases, the call will fail, alerting your team that
        someone is trying to make a change that requires a migration and
        that migration is absent.
        """
        logger.info("")
        result = call_command("makemigrations", check=True, dry_run=True)
        assert not result


# class MetricTests(TestCase):
#
#     def test_metrics(self):
#         logger.info('# Installed Apps: ' + str(len(apps.get_app_configs())))
#         current_apps = apps.get_app_configs()
#         for app in current_apps:
#             logger.info('Apps: ' + str(app))
#         logger.info('# Models: ' + str(len(apps.get_models())))
#         current_models = apps.get_models()
#         for model in current_models:
#             logger.info('Models: ' + str(model))
