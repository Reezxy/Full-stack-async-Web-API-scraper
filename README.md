# Full-stack Async Web API Scraper

A small full-stack web scraper: an **async Django API** that fetches a URL with
retry and backoff and stores the result, plus a **Nuxt 4** frontend to submit
URLs and inspect the scraped HTML.

## Stack

- **Backend:** Django 6 (async views), Django REST Framework, httpx, django-cors-headers
- **Frontend:** Nuxt 4, Nuxt UI 4, Pinia, Tailwind, TypeScript, zod

## Project structure

```
DjangoProject/
├── app/
│   ├── API/              # async view + request serializer
│   ├── Application/      # scraper service, interfaces, exceptions
│   ├── Infrastructure/   # httpx fetcher, repository, factory
│   ├── models.py         # ScrapeResult model
│   └── tests/unit_tests/
├── settings.py
└── urls.py
frontend/                 # Nuxt app (form, result view, Pinia store)
```

## Getting started

```bash
# Backend: http://localhost:8000
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend: http://localhost:3000
cd frontend
npm install
npm run dev
```

The frontend needs Node 22 or newer and reads the API URL from
`NUXT_PUBLIC_SCRAPER_API_URL` (default `http://localhost:8000`). For anything beyond local development, set
`DJANGO_SECRET_KEY`.

## API

`POST /scrape/`

```json
{ "url": "https://example.com", "call_count": 3 }
```

| Status    | Body                                                              |
|-----------|-------------------------------------------------------------------|
| 201       | `{"status": <http_status>, "success": <bool>, "content": "<html>"}` |
| 400 / 422 | `{"error": "<message>"}`                                          |
| 500       | `{"error": "Internal server error"}`                              |

`call_count` is the maximum number of fetch attempts. A 201 does not mean the
scrape succeeded: `success` is `false` when the target site answered with a
non-2xx status. Every result (URL, status code, first 500 characters of
content, success flag, timestamp) is stored in the database.

## Quality checks

```bash
python manage.py test DjangoProject.app.tests

cd frontend
npm run lint
npm run typecheck
```

## License

[MIT](LICENSE)
