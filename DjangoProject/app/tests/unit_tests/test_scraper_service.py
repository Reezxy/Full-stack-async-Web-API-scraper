from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from DjangoProject.app.Application.Scraper.exceptions import FetchError, ScrapeFailedError
from DjangoProject.app.Application.Scraper.service import ScraperService, is_success_status

from .fakes import InMemoryRepository, ScriptedFetcher, ok

URL = "https://example.com"


class IsSuccessStatusTests(IsolatedAsyncioTestCase):
    def test_2xx_range_is_success(self):
        for code in (200, 201, 204, 299):
            self.assertTrue(is_success_status(code), code)

    def test_everything_else_is_failure(self):
        for code in (100, 199, 300, 301, 404, 429, 500, 503):
            self.assertFalse(is_success_status(code), code)


class ScraperServiceTests(IsolatedAsyncioTestCase):
    def make_service(self, *results):
        fetcher = ScriptedFetcher(*results)
        repository = InMemoryRepository()
        return ScraperService(fetcher, repository), fetcher, repository

    async def test_success_on_first_attempt_stops_retrying(self):
        service, fetcher, repository = self.make_service(ok())

        outcome = await service.scrape(URL, call_count=3)

        self.assertTrue(outcome.success)
        self.assertEqual(outcome.status_code, 200)
        self.assertEqual(outcome.content, "<html>ok</html>")
        self.assertEqual(outcome.attempts, 1)
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(repository.saved, [
            {"url": URL, "status_code": 200, "content": "<html>ok</html>", "success": True}
        ])

    async def test_retries_non_2xx_until_success(self):
        service, fetcher, repository = self.make_service(
            ok("down", 503), ok("down", 502), ok("<html>up</html>", 200)
        )

        outcome = await service.scrape(URL, call_count=5)

        self.assertTrue(outcome.success)
        self.assertEqual(outcome.attempts, 3)
        self.assertEqual(len(fetcher.calls), 3)
        self.assertEqual(len(repository.saved), 1)
        self.assertEqual(repository.saved[0]["status_code"], 200)

    async def test_all_attempts_fail_returns_and_stores_last_response(self):
        service, fetcher, repository = self.make_service(ok("a", 500), ok("b", 404))

        outcome = await service.scrape(URL, call_count=2)

        self.assertFalse(outcome.success)
        self.assertEqual(outcome.status_code, 404)
        self.assertEqual(outcome.content, "b")
        self.assertEqual(outcome.attempts, 2)
        self.assertEqual(repository.saved, [
            {"url": URL, "status_code": 404, "content": "b", "success": False}
        ])

    async def test_network_errors_are_retried(self):
        service, fetcher, repository = self.make_service(
            FetchError("timeout"), FetchError("connection reset"), ok()
        )

        outcome = await service.scrape(URL, call_count=3)

        self.assertTrue(outcome.success)
        self.assertEqual(outcome.attempts, 3)

    async def test_last_http_response_wins_over_later_network_error(self):
        service, _, repository = self.make_service(ok("err", 500), FetchError("timeout"))

        outcome = await service.scrape(URL, call_count=2)

        self.assertFalse(outcome.success)
        self.assertEqual(outcome.status_code, 500)
        self.assertEqual(len(repository.saved), 1)

    async def test_no_response_at_all_raises_and_stores_nothing(self):
        service, fetcher, repository = self.make_service(FetchError("dns"), FetchError("dns"))

        with self.assertRaises(ScrapeFailedError) as ctx:
            await service.scrape(URL, call_count=2)

        self.assertEqual(ctx.exception.attempts, 2)
        self.assertIn("after 2 attempts", str(ctx.exception))
        self.assertEqual(repository.saved, [])

    async def test_call_count_below_one_is_rejected(self):
        service, _, _ = self.make_service()
        with self.assertRaises(ValueError):
            await service.scrape(URL, call_count=0)


class BackoffTests(IsolatedAsyncioTestCase):
    async def test_waits_with_exponential_backoff_between_attempts(self):
        service = ScraperService(
            ScriptedFetcher(ok("x", 500), ok("x", 500), ok("x", 500), ok()),
            InMemoryRepository(),
            backoff_base_seconds=0.5,
            backoff_max_seconds=1.5,
        )

        with patch("DjangoProject.app.Application.Scraper.service.asyncio.sleep") as sleep:
            await service.scrape(URL, call_count=4)

        self.assertEqual([c.args[0] for c in sleep.await_args_list], [0.5, 1.0, 1.5])

    async def test_no_wait_after_the_final_attempt(self):
        service = ScraperService(
            ScriptedFetcher(ok("x", 500)), InMemoryRepository(), backoff_base_seconds=1, backoff_max_seconds=1
        )

        with patch("DjangoProject.app.Application.Scraper.service.asyncio.sleep") as sleep:
            await service.scrape(URL, call_count=1)

        sleep.assert_not_awaited()
