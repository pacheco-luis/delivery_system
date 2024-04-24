from typing import Any
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        from datetime import datetime
        print( 'NotificationsConfig ready:', datetime.now() )
        import notifications.signals
    