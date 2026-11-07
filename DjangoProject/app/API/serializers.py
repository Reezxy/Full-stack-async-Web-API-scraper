from django.core.validators import URLValidator
from rest_framework import serializers

MAX_CALL_COUNT = 10


class ScrapeRequestSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=2048, validators=[URLValidator(schemes=["http", "https"])])
    call_count = serializers.IntegerField(min_value=1, max_value=MAX_CALL_COUNT)


def flatten_errors(errors: dict) -> str:
    """Turn DRF's nested error dict into one readable message."""
    parts = []
    for field, messages in errors.items():
        text = " ".join(str(m) for m in messages) if isinstance(messages, list) else str(messages)
        parts.append(text if field == "non_field_errors" else f"{field}: {text}")
    return " ".join(parts)
