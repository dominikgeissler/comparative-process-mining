from django.contrib import admin
from .models import Log, LogObjectHandler

admin.site.register(Log)
admin.site.register(LogObjectHandler)
