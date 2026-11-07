from django.contrib import admin

from .models import ScrapeResult


@admin.register(ScrapeResult)
class ScrapeResultAdmin(admin.ModelAdmin):
    list_display = ("url", "status_code", "success", "created_at")
    list_filter = ("success", "status_code")
    search_fields = ("url",)
    readonly_fields = ("url", "status_code", "content_preview", "success", "created_at")
