from DjangoProject.app.Application.Scraper.exceptions import FetchError
from DjangoProject.app.Application.Scraper.interfaces import FetchResponse


class ScriptedFetcher:
    """Returns (or raises) the queued results in order, recording each call."""

    def __init__(self, *results: FetchResponse | FetchError):
        self._results = list(results)
        self.calls: list[str] = []

    async def fetch(self, url: str) -> FetchResponse:
        self.calls.append(url)
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class InMemoryRepository:
    def __init__(self):
        self.saved: list[dict] = []

    async def save(self, *, url: str, status_code: int, content: str, success: bool) -> None:
        self.saved.append(
            {"url": url, "status_code": status_code, "content": content, "success": success}
        )


def ok(content: str = "<html>ok</html>", status: int = 200) -> FetchResponse:
    return FetchResponse(status_code=status, content=content)
