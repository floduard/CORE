from django.contrib import admin
from .models import *


admin.site.site_header = "Cybercrime Admin Panel"
admin.site.site_title = "Cybercrime Admin Portal"
admin.site.index_title = "Cybercrime Reporting Admin"


admin.site.register(User)
admin.site.register(Notification)
admin.site.register(ActivityLog)
admin.site.register(UserMFA)