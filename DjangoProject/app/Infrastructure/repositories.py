from DjangoProject.app.models import ScrapeResult


class DjangoScrapeResultRepository:
    """ScrapeResultRepository implementation using the Django async ORM."""

    async def save(self, *, url: str, status_code: int, content: str, success: bool) -> None:
        await ScrapeResult.objects.acreate(
            url=url,
            status_code=status_code,
            content_preview=content[: ScrapeResult.CONTENT_PREVIEW_LENGTH],
            success=success,
        )
