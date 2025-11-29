from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Django app ready hook - runs when the app is loaded.
        Start the APScheduler here for automatic tasks.
        """
        # Import signals
        import accounts.signals
        
        # Start the scheduler (only in production/runserver, not in migrations)
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            # Prevent duplicate initialization in Django dev server (reloader)
            if os.environ.get('RUN_MAIN') != 'true':
                return
                
            try:
                from accounts.scheduler import start_scheduler
                start_scheduler()
                logger.info("Attendance scheduler initialized successfully")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")