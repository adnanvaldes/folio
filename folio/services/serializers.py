from typing import Dict, Any

from models.models import Work
from services.protocols import Serializer


class WorkSerializer(Serializer[Work]):
    def to_dict(self, record: Work) -> Dict[str, Any]:
        return {
            "id": record.id,
            "title": record.title,
            "author": record.author,
            "year": record.year,
            "genre": record.genre,
            "is_read": record.is_read,
        }

    def from_dict(self, data: Dict[str, Any]) -> Work:
        return Work(
            id=data.get("id"),
            title=data.get("title", ""),
            author=data.get("author", ""),
            year=data.get("year"),
            genre=data.get("genre", ""),
            is_read=bool(data.get("is_read", False)),
        )
