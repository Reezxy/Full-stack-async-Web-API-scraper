from django.db import models


class ScrapeResult(models.Model):
    CONTENT_PREVIEW_LENGTH = 500

    url = models.URLField(max_length=2048)
    status_code = models.PositiveSmallIntegerField()
    content_preview = models.CharField(max_length=CONTENT_PREVIEW_LENGTH, blank=True)
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.url} [{self.status_code}]"
