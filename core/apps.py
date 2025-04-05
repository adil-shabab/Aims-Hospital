# core/apps.py

from django.apps import AppConfig
from pytz import timezone as pytz_timezone

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals
        from core.tasks import send_daily_doctor_appointments_sms
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        import logging

        logger = logging.getLogger(__name__)

        scheduler = BackgroundScheduler()

        if not hasattr(self, 'scheduler_started'):
            logger.info("Starting the scheduler for daily doctor appointment reminders.")

            # Schedule the task at 10:00 AM every day using local timezone
            scheduler.add_job(
                send_daily_doctor_appointments_sms,
                CronTrigger(hour=10, minute=43, timezone=pytz_timezone('Asia/Kolkata')),
            )

            scheduler.start()
            self.scheduler_started = True
            logger.info("Scheduler for daily doctor appointment reminders started.")
