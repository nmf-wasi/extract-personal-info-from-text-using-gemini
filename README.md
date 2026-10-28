# Personal Data Extractor API

A small FastAPI service that turns the text of a person's description into validated JSON, using Gemini structured outputs. Send messy text, get typed fields back, or a clear error when the input or the model output can't be used.

## Example

```bash
curl -X POST http://127.0.0.1:8000/person/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Wasi was born 20 years ago, in Dhaka, later moved to Seoul in 2025."}'
```

```json
{
    "is_personal_info": true,
    "name": "Wasi",
    "age": 20,
    "birthplace": "Dhaka"
}
```

Fields that are not in the text come back as `null` instead of being invented.

## Endpoints

| Route                  | Description                          |
| ---------------------- | ------------------------------------ |
| `POST /person/extract` | Extract structured fields from texts |
| `GET /health`          | Health check                         |

### Status codes for `/person/extract`

| Code | Meaning                                                                  |
| ---- | ------------------------------------------------------------------------ |
| 200  | Extraction succeeded                                                     |
| 422  | Empty or invalid request body, or the text is not a person's description |
| 502  | The model returned unusable output (for example, a truncated response)   |
| 503  | Gemini is unavailable or over quota, retry later                         |

## Setup

```bash
git clone https://github.com/nmf-wasi/extract-personal-info-from-text-using-gemini
cd extract-personal-info-from-text-using-gemini
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your Gemini API key in .env
uvicorn app.src.main:app --reload
```

Interactive docs are at `http://127.0.0.1:8000/docs`.

## Tests

```bash
pytest
```

The tests never call Gemini. The route gets its extractor through a FastAPI dependency (`get_extractor`), and the tests override it with a fake that returns a posting or raises an error. That lets them check the validation, the `is_personal_info` check and the error-to-status-code mapping in about a second, with no API key and no quota.

## Design

- Only `app/llm.py` talks to Gemini. Everything else sees a `PersonalInfo` or one of two exceptions (`LLMBadOutput`, `LLMUnavailable`)
- The `PersonalInfo` schema is passed to Gemini as `response_schema`, and the same class is the API's response model
- Nullable fields and an `is_personal_info` flag give the model an honest way to say "not in the text" or "this is not personal data"
- The route is a plain `def`, not `async def`, because the Gemini call is synchronous

## Project layout

```
.
├── app/
│   ├── routers/
│   │   └── person.py       # POST /person/extract and error mapping
│   ├── schemas/
│   │   └── person.py       # PersonalInfo response schema & age validation
│   ├── src/
│   │   └── main.py         # FastAPI app instantiation, /health, router registration
│   └── llm.py              # Gemini client wrapper (the only file that talks to Gemini)
├── test/
│   ├── conftest.py         # Pytest fixtures and configurations
│   └── test_person.py      # Pytest suite with mock/fake extractor tests
├── .env.example            # Environment variable template
├── .gitignore
├── pytest.ini              # Pytest configuration settings
├── README.md               # Project documentation
└── requirements.txt        # Project dependencies
```

## Known limitations

- The model decides what counts as a personal data, so edge cases depend on its judgment
- The tests use a fake extractor, so the logic inside `llm.py` (turning Gemini errors and unparseable output into the two exceptions) is not covered by automated tests
- The free tier has request limits, which show up as 503 responses
- No authentication, rate limiting or database
