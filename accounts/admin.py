from django.contrib import admin
from .models import Apartment, WebUser, MaintenanceRequest, Chat

admin.site.register(Apartment)
admin.site.register(WebUser)
admin.site.register(MaintenanceRequest)


