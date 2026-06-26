from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api import create_app


def test_watch_api_accepts_training_metadata_without_full_content():
    path = Path("outputs") / f"test-api-watch-{uuid4()}.json"
    client = TestClient(create_app(path))

    try:
        response = client.post(
            "/api/watch-items",
            json={
                "url": "https://openclassrooms.com/fr/courses/angular",
                "title": "Approfondir Angular moderne",
                "item_type": "training",
                "tags": ["Angular", "Frontend"],
                "related_skill": "Angular",
                "captured_at": "2026-05-05T10:00:00",
            },
        )

        assert response.status_code == 201
        assert response.json()["item_type"] == "training"
        assert response.json()["source"] == "openclassrooms"
        assert "content" not in response.json()

        list_response = client.get("/api/watch-items?item_type=training")

        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
    finally:
        path.unlink(missing_ok=True)
