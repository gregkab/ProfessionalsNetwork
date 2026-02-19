from django.contrib import admin

from .models import Professional


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("full_name", "email", "phone")
