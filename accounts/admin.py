from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(CitizenProfile)
admin.site.register(OfficerProfile)
admin.site.register(AdminProfile)
admin.site.register(Notification)
admin.site.register(ActivityLog)