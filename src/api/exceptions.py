import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _flatten_errors(data: object) -> str:
    if isinstance(data, dict):
        if "detail" in data and len(data) == 1:
            return str(data["detail"])
        parts = []
        for field, value in data.items():
            if isinstance(value, (list, tuple)):
                parts.append(f"{field}: {', '.join(str(v) for v in value)}")
            else:
                parts.append(f"{field}: {value}")
        return "; ".join(parts)
    if isinstance(data, (list, tuple)):
        return "; ".join(str(v) for v in data)
    return str(data)


def custom_exception_handler(exc: Exception, context: dict[str, object]) -> Response:
    response = exception_handler(exc, context)
    if response is not None:
        return Response(
            {"error": _flatten_errors(response.data)},
            status=response.status_code,
            headers=response.headers,
        )

    if isinstance(exc, ObjectDoesNotExist):
        model_name = getattr(exc, "model_name", "Object")
        return Response({"error": f"{model_name} not found"}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, IntegrityError):
        # 🆕 Записываем в лог причину падения ограничений базы данных
        logger.warning(f"Database integrity constraint violated: {exc}")
        return Response(
            {"error": "Database constraint violation (e.g. duplicate key or restrict constraint)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Все остальные непредвиденные ошибки (500) записываются со стеком вызовов
    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {"error": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
