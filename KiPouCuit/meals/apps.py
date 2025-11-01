from django.apps import AppConfig
from django.db.models.signals import post_migrate

class MealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meals'

    def ready(self):
        from .models import MenuItem
        def populate(sender, **kwargs):
            if not MenuItem.objects.exists():
            
                pass
        post_migrate.connect(populate, sender=self)
