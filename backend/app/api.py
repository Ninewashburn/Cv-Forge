"""Local HTTP API for CVForge.

The API is intentionally local-first. Browser addons, manual imports or future
RSS jobs can send minimal metadata to CVForge without transferring full job
posts or duplicating external content.
"""

from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .bookmark_store import BookmarkStore, create_bookmark
from .watch_store import WatchStore, create_watch_item


class BookmarkPayload(BaseModel):
    url: str = Field(min_length=1)
    title: str = ""
    company: str = ""
    source: Optional[str] = None
    captured_at: Optional[str] = None
    status: Optional[str] = "bookmarked"


class WatchItemPayload(BaseModel):
    url: str = Field(min_length=1)
    title: str = ""
    source: Optional[str] = None
    item_type: Optional[str] = "offer"
    captured_at: Optional[str] = None
    status: Optional[str] = "bookmarked"
    company: Optional[str] = None
    tags: List[str] = []
    related_skill: Optional[str] = None


def create_app(store_path: Path = Path("data/watch_items.json")) -> FastAPI:
    app = FastAPI(title="CVForge Local API")
    watch_store = WatchStore(store_path)
    bookmark_store = BookmarkStore(store_path)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ],
        allow_origin_regex=r"^(chrome-extension|moz-extension)://.*$",
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/watch-items")
    def list_watch_items(
        source: Optional[str] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[dict[str, object]]:
        return [
            asdict(item)
            for item in watch_store.list(source=source, item_type=item_type, status=status)
        ]

    @app.post("/api/watch-items", status_code=201)
    def save_watch_item(payload: WatchItemPayload) -> dict[str, object]:
        item = create_watch_item(**payload.model_dump())
        return asdict(watch_store.upsert(item))

    @app.get("/api/bookmarks")
    def list_bookmarks(source: Optional[str] = None, status: Optional[str] = None) -> list[dict[str, str]]:
        return [asdict(bookmark) for bookmark in bookmark_store.list(source=source, status=status)]

    @app.post("/api/bookmarks", status_code=201)
    def save_bookmark(payload: BookmarkPayload) -> dict[str, str]:
        bookmark = create_bookmark(**payload.model_dump())
        return asdict(bookmark_store.upsert(bookmark))

    return app


app = create_app()
