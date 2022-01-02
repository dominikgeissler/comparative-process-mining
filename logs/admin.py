from django.contrib import admin
from .models import Log, LogObjectHandler, Filter

admin.site.register(Log)
admin.site.register(LogObjectHandler)
admin.site.register(Filter)
