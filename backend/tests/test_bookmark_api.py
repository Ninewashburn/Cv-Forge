from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api import create_app


def test_bookmark_api_saves_and_lists_metadata_only():
    path = Path("outputs") / f"test-api-bookmarks-{uuid4()}.json"
    client = TestClient(create_app(path))

    try:
        response = client.post(
            "/api/bookmarks",
            json={
                "url": "https://www.hellowork.com/fr-fr/emplois/123.html",
                "title": "Développeur Angular",
                "company": "Entreprise exemple",
                "captured_at": "2026-05-04T14:30:00",
                "status": "bookmarked",
            },
        )

        assert response.status_code == 201
        assert response.json() == {
            "url": "https://www.hellowork.com/fr-fr/emplois/123.html",
            "title": "Développeur Angular",
            "company": "Entreprise exemple",
            "source": "hellowork",
            "captured_at": "2026-05-04T14:30:00",
            "status": "bookmarked",
        }

        list_response = client.get("/api/bookmarks?source=hellowork")

        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        assert "content" not in list_response.json()[0]
    finally:
        path.unlink(missing_ok=True)
