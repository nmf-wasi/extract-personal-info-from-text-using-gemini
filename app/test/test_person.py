from app.llm import LLMBadOutput, LLMUnavailable
from app.schemas.person import PersonalInfo


def test_valid_person(client, use_fake):
    def fake(test):
        return PersonalInfo(
            is_personal_info=True,
            name="nmf wasi",
            age=20,
            birthplace="Dhaka",
        )

    use_fake(fake)
    response = client.post("/person/extract", json={"text": "anything"})
    assert response.status_code == 200
    assert response.json()["name"] == "nmf wasi"


def test_llm_unavailable_return_503(client, use_fake):
    def fake(text):
        raise LLMUnavailable("quota")

    use_fake(fake)
    response = client.post("/person/extract", json={"text": "anything"})
    assert response.status_code == 503


def test_not_personal_info_returns_422(client, use_fake):
    def fake(text):
        return PersonalInfo(
            is_personal_info=False,
            name=None,
            age=None,
            birthplace=None,
        )

    use_fake(fake)
    response = client.post("/person/extract", json={"text": "anything"})
    assert response.status_code == 422


def test_bad_llm_output(client, use_fake):
    def fake(text):
        raise LLMBadOutput("MAX_TOKENS")

    use_fake(fake)
    response = client.post("/person/extract", json={"text": "anything"})
    assert response.status_code == 502


def test_empty_test_returns_422(client):
    response = client.post("/person/extract", json={"text": ""})
    assert response.status_code == 422


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
