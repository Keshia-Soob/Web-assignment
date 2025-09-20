# from django.apps import AppConfig


# class AdminConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'admin'
from django.apps import AppConfig

class AdminPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'
    label = 'admin_panel_app'  # <-- add this line to give it a unique label
