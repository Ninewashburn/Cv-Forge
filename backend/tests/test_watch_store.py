from pathlib import Path
from uuid import uuid4

from app.watch_store import WatchStore, create_watch_item


def test_watch_store_tracks_multiple_resource_types():
    path = Path("outputs") / f"test-watch-items-{uuid4()}.json"
    store = WatchStore(path)
    offer = create_watch_item(
        url="https://www.hellowork.com/fr-fr/emplois/123.html",
        title="Développeur Angular",
        company="Entreprise A",
        item_type="offer",
        tags=["Angular", "Frontend", "Angular"],
        captured_at="2026-05-05T09:00:00",
    )
    training = create_watch_item(
        url="https://openclassrooms.com/fr/courses/angular",
        title="Approfondir Angular",
        item_type="training",
        related_skill="Angular",
        captured_at="2026-05-05T10:00:00",
    )

    try:
        store.upsert(offer)
        store.upsert(training)

        assert [item.item_type for item in store.list()] == ["training", "offer"]
        assert [item.source for item in store.list(item_type="training")] == ["openclassrooms"]
        assert store.list(item_type="offer")[0].tags == ["angular", "frontend"]
    finally:
        path.unlink(missing_ok=True)
