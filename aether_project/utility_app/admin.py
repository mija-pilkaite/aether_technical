from django.contrib import admin
from .models import Project
# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('address', 'kWh_consumption', 'escalator')
    search_fields = ('address',)

admin.site.register(Project, ProjectAdmin)
