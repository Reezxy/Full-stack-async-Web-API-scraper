from django.conf import settings

from DjangoProject.app.Application.Scraper.service import ScraperService

from .http_client import HttpxFetcher
from .repositories import DjangoScrapeResultRepository


def build_scraper_service() -> ScraperService:
    config = settings.SCRAPER
    return ScraperService(
        fetcher=HttpxFetcher(
            timeout_seconds=config["TIMEOUT_SECONDS"],
            max_content_bytes=config["MAX_CONTENT_BYTES"],
        ),
        repository=DjangoScrapeResultRepository(),
        backoff_base_seconds=config["BACKOFF_BASE_SECONDS"],
        backoff_max_seconds=config["BACKOFF_MAX_SECONDS"],
    )
