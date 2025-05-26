from django.contrib import admin
# Register your models here.
from .models import *

admin.site.register(CybercrimeType)
admin.site.register(CybercrimeReport)
admin.site.register(CaseAssignmentHistory)
admin.site.register(AdditionalEvidence)
 
