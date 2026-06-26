"""Local storage for the candidature watch center.

The watch center stores user-selected metadata for offers, trainings, news,
events and application records. It avoids copying full external content so
CVForge stays a personal cockpit rather than a job board clone.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse

from .models import WatchItem

DEFAULT_WATCH_ITEMS_PATH = Path("data/watch_items.json")

ALLOWED_TYPES = {"offer", "training", "news", "event", "application"}
ALLOWED_STATUSES = {
    "bookmarked",
    "to_analyze",
    "analyzing",
    "ready",
    "applied",
    "follow_up",
    "registered",
    "read",
    "archived",
}

SOURCE_BY_DOMAIN = {
    "hellowork.com": "hellowork",
    "indeed.com": "indeed",
    "apec.fr": "apec",
    "welcometothejungle.com": "welcome-to-the-jungle",
    "linkedin.com": "linkedin",
    "francetravail.fr": "france-travail",
    "pole-emploi.fr": "france-travail",
    "openclassrooms.com": "openclassrooms",
    "coursera.org": "coursera",
    "meetup.com": "meetup",
}


def infer_source(url: str, explicit_source: Optional[str] = None) -> str:
    """Return a normalized source from an explicit value or the item URL."""
    if explicit_source:
        return explicit_source.strip().lower()

    hostname = (urlparse(url).hostname or "").lower().removeprefix("www.")
    for domain, source in SOURCE_BY_DOMAIN.items():
        if hostname == domain or hostname.endswith(f".{domain}"):
            return source
    return "other"


def normalize_item_type(item_type: Optional[str]) -> str:
    """Keep item types constrained to the watch center taxonomy."""
    normalized = (item_type or "offer").strip().lower()
    return normalized if normalized in ALLOWED_TYPES else "offer"


def normalize_status(status: Optional[str]) -> str:
    """Keep persisted statuses constrained to known workflow states."""
    normalized = (status or "bookmarked").strip().lower()
    return normalized if normalized in ALLOWED_STATUSES else "bookmarked"


def normalize_tags(tags: Optional[Iterable[str]]) -> List[str]:
    """Trim tags and remove empty or duplicated values."""
    normalized: List[str] = []
    for tag in tags or []:
        value = tag.strip().lower()
        if value and value not in normalized:
            normalized.append(value)
    return normalized


def create_watch_item(
    *,
    url: str,
    title: str,
    source: Optional[str] = None,
    item_type: Optional[str] = "offer",
    captured_at: Optional[str] = None,
    status: Optional[str] = None,
    company: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    related_skill: Optional[str] = None,
) -> WatchItem:
    """Create a sanitized watch item from addon, RSS, import or UI metadata."""
    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("A watch item URL is required.")

    return WatchItem(
        url=cleaned_url,
        title=title.strip() or "Ressource sans titre",
        source=infer_source(cleaned_url, source),
        item_type=normalize_item_type(item_type),
        captured_at=captured_at or datetime.now().isoformat(timespec="seconds"),
        status=normalize_status(status),
        company=company.strip() if company else None,
        tags=normalize_tags(tags),
        related_skill=related_skill.strip() if related_skill else None,
    )


class WatchStore:
    """Read and write watch items in a local JSON file."""

    def __init__(self, path: Path = DEFAULT_WATCH_ITEMS_PATH):
        self.path = path

    def list(
        self,
        source: Optional[str] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[WatchItem]:
        items = self._read()
        if source:
            items = [item for item in items if item.source == source]
        if item_type:
            normalized_type = normalize_item_type(item_type)
            items = [item for item in items if item.item_type == normalized_type]
        if status:
            normalized_status = normalize_status(status)
            items = [item for item in items if item.status == normalized_status]
        return sorted(items, key=lambda item: item.captured_at, reverse=True)

    def upsert(self, item: WatchItem) -> WatchItem:
        items = [stored for stored in self._read() if stored.url != item.url]
        items.append(item)
        self._write(items)
        return item

    def _read(self) -> List[WatchItem]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            WatchItem(
                url=item["url"],
                title=item["title"],
                source=item["source"],
                item_type=item.get("item_type", "offer"),
                captured_at=item["captured_at"],
                status=item.get("status", "bookmarked"),
                company=item.get("company"),
                tags=item.get("tags", []),
                related_skill=item.get("related_skill"),
            )
            for item in data
        ]

    def _write(self, items: Iterable[WatchItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(item) for item in items]
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
