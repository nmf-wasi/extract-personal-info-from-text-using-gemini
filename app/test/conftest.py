import pytest
from fastapi.testclient import TestClient

from app.src.main import app
from app.routers.person import get_extractor


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def use_fake():
    def _use(fake):
        app.dependency_overrides[get_extractor] = lambda: fake

    return _use
