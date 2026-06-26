from pathlib import Path
from uuid import uuid4

from app.bookmark_store import BookmarkStore, create_bookmark, infer_source


def test_infer_source_from_known_job_board_url():
    assert infer_source("https://www.hellowork.com/fr-fr/emplois/123.html") == "hellowork"
    assert infer_source("https://www.apec.fr/candidat/recherche-emploi") == "apec"
    assert infer_source("https://www.linkedin.com/jobs/view/123") == "linkedin"


def test_store_upserts_by_url_and_filters():
    path = Path("outputs") / f"test-bookmarks-{uuid4()}.json"
    store = BookmarkStore(path)
    first = create_bookmark(
        url="https://www.hellowork.com/fr-fr/emplois/123.html",
        title="Développeur Laravel",
        company="Entreprise A",
        captured_at="2026-05-04T14:30:00",
    )
    updated = create_bookmark(
        url="https://www.hellowork.com/fr-fr/emplois/123.html",
        title="Développeur Laravel Angular",
        company="Entreprise A",
        captured_at="2026-05-05T09:00:00",
        status="ready",
    )
    other = create_bookmark(
        url="https://www.apec.fr/offre/456",
        title="Ingénieur Python",
        company="Entreprise B",
        captured_at="2026-05-04T16:00:00",
    )

    try:
        store.upsert(first)
        store.upsert(updated)
        store.upsert(other)

        all_bookmarks = store.list()
        assert len(all_bookmarks) == 2
        assert all_bookmarks[0].title == "Développeur Laravel Angular"
        assert [bookmark.source for bookmark in store.list(source="apec")] == ["apec"]
        assert [bookmark.status for bookmark in store.list(status="ready")] == ["ready"]
    finally:
        path.unlink(missing_ok=True)
