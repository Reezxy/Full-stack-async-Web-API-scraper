import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from DjangoProject.app.API.serializers import ScrapeRequestSerializer, flatten_errors
from DjangoProject.app.Application.Scraper.exceptions import ScrapeFailedError
from DjangoProject.app.Infrastructure.factory import build_scraper_service

logger = logging.getLogger(__name__)


def error_response(message: str, status: int) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


@csrf_exempt
@require_POST
async def scrape_view(request: HttpRequest) -> JsonResponse:
    # 400: the request body itself is unusable.
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return error_response("Request body must be valid JSON.", 400)
    if not isinstance(payload, dict):
        return error_response("Request body must be a JSON object.", 400)

    # 422: well formed JSON, but the values are not acceptable.
    serializer = ScrapeRequestSerializer(data=payload)
    if not serializer.is_valid():
        return error_response(flatten_errors(serializer.errors), 422)

    url = serializer.validated_data["url"]
    call_count = serializer.validated_data["call_count"]

    try:
        outcome = await build_scraper_service().scrape(url, call_count)
    except ScrapeFailedError as exc:
        return error_response(str(exc), 422)
    except Exception:
        logger.exception("Unexpected error while scraping %s", url)
        return error_response("Internal server error", 500)

    return JsonResponse(
        {"status": outcome.status_code, "success": outcome.success, "content": outcome.content},
        status=201,
    )
