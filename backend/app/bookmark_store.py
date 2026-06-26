"""Compatibility layer for job offer bookmarks.

New code should use watch_store for the broader candidature watch center. This
module keeps the original bookmark API focused on job offers for the browser
addon.
"""

from pathlib import Path
from typing import List, Optional

from .models import JobBookmark
from .watch_store import (
    DEFAULT_WATCH_ITEMS_PATH,
    WatchStore,
    create_watch_item,
    infer_source,
    normalize_status,
)

DEFAULT_BOOKMARKS_PATH = DEFAULT_WATCH_ITEMS_PATH


def create_bookmark(
    *,
    url: str,
    title: str,
    company: str,
    source: Optional[str] = None,
    captured_at: Optional[str] = None,
    status: Optional[str] = None,
) -> JobBookmark:
    """Create a sanitized offer bookmark from addon or UI metadata."""
    item = create_watch_item(
        url=url,
        title=title,
        company=company or "Entreprise non renseignée",
        source=source,
        item_type="offer",
        captured_at=captured_at,
        status=status,
    )
    return JobBookmark(
        url=item.url,
        title=item.title,
        company=item.company or "Entreprise non renseignée",
        source=item.source,
        captured_at=item.captured_at,
        status=item.status,
    )


class BookmarkStore:
    """Offer-only view over the broader watch store."""

    def __init__(self, path: Path = DEFAULT_BOOKMARKS_PATH):
        self.store = WatchStore(path)

    def list(self, source: Optional[str] = None, status: Optional[str] = None) -> List[JobBookmark]:
        items = self.store.list(source=source, item_type="offer", status=status)
        return [
            JobBookmark(
                url=item.url,
                title=item.title,
                company=item.company or "Entreprise non renseignée",
                source=item.source,
                captured_at=item.captured_at,
                status=item.status,
            )
            for item in items
        ]

    def upsert(self, bookmark: JobBookmark) -> JobBookmark:
        item = create_watch_item(
            url=bookmark.url,
            title=bookmark.title,
            company=bookmark.company,
            source=bookmark.source,
            item_type="offer",
            captured_at=bookmark.captured_at,
            status=bookmark.status,
        )
        self.store.upsert(item)
        return bookmark
