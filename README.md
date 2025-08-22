# Django + React CRA/Vite SPA Integration

This project demonstrates how to serve a **React SPA (CRA or Vite)** from a **Django backend**.  
The goal: use Django to serve the frontend entrypoint and static files, while keeping a smooth developer experience (HMR in dev, manifest-based assets in prod).

---

## Project Structure

```
.
├── backend/                 # Django project
│   ├── core/                # Example app
│   ├── web/                 # Django settings/urls/asgi/wsgi
│   ├── templates/
│   │   └── index.html       # Base entrypoint
│   └── manage.py
├── frontend/                # CRA or Vite frontend
│   ├── src/
│   ├── public/
│   ├── build/               # CRA build output (npm run build)
│   ├── dist/                # Vite build output (npm run build)
│   └── package.json
└── requirements.txt
```

---

## Django Setup

### Settings
```python
# web/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    ...,
    "django.contrib.staticfiles",
    "core",  # your app
]

TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "build" / "static",  # CRA build artifacts
    # or BASE_DIR / "frontend" / "dist" for Vite
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# For dev HMR injection
DEV_MODE = os.getenv("DEV_MODE", "0") == "1"
FRONTEND_DEV_SERVER_URL = os.getenv("FRONTEND_DEV_SERVER_URL", "http://localhost:5173")
```

### View
```python
# core/views.py
from django.views.generic import TemplateView
from django.conf import settings

class AppView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["DEV_MODE"] = settings.DEV_MODE
        ctx["DEV_SERVER_URL"] = settings.FRONTEND_DEV_SERVER_URL
        # expose safe public config if needed
        return ctx
```

### URLs
```python
# web/urls.py
from django.urls import path
from core.views import AppView

urlpatterns = [
    path("", AppView.as_view(), name="spa-entry"),
]
```

---

## Template

`templates/index.html` decides which assets to load:

```html
{% load static cra %}
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>My App</title>

    <!-- Public runtime config -->
    <script>
      window.__APP_CONFIG__ = {
        apiUrl: "{{ API_URL|default:'/api/' }}",
        env: "{{ ENV|default:'dev' }}"
      }
    </script>

    {% if DEV_MODE and DEV_SERVER_URL %}
      <!-- Vite dev server -->
      <script type="module" src="{{ DEV_SERVER_URL }}/@vite/client"></script>
      <script type="module" src="{{ DEV_SERVER_URL }}/src/main.tsx"></script>
    {% else %}
      <!-- Production build (CRA/Vite) -->
      {% cra_css_tags %}
      {% cra_js_tags %}
    {% endif %}
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

---

## Static Assets Handling

- **Production**:  
  - `npm run build` → CRA outputs to `frontend/build`, Vite to `frontend/dist`.  
  - Django loads asset paths from the `manifest.json` and renders correct `<script>/<link>` tags.  
  - Run `python manage.py collectstatic` to copy into `STATIC_ROOT`.

- **Hashing**:  
  - Filenames (e.g. `main.abc123.css`) are managed by the frontend bundler.  
  - Django serves them via `ManifestStaticFilesStorage`.

---

## Development with Hot Module Reload

### Option 1: Run frontend separately
- CRA: `npm start` (http://localhost:3000)  
- Vite: `npm run dev` (http://localhost:5173)  
- Use a proxy in `package.json` (CRA) or `vite.config.ts` (Vite) to forward `/api` to Django.

### Option 2: Serve frontend through Django with injected scripts
Set environment variables:
```bash
DEV_MODE=1
FRONTEND_DEV_SERVER_URL=http://localhost:5173
```

Then start both servers:
```bash
python backend/manage.py runserver
cd frontend && npm run dev
```

Visit http://localhost:8000 and Django will inject Vite’s HMR scripts.

---

## Environment Variables

Pass **public** config (safe to expose in frontend) through Django:
```python
ctx["API_URL"] = settings.API_URL
ctx["ENV"] = settings.ENV
```

Sensitive secrets (API keys, DB passwords, etc.) **must stay server-side**.

---

## Deployment

1. Build frontend (`npm run build`).
2. Run Django `collectstatic`.
3. Deploy Django app + staticfiles via your WSGI/ASGI server (Gunicorn, Daphne, etc.).
4. Serve static assets via WhiteNoise, Nginx, or CDN.

---

## Notes

- Use **Vite** if possible: faster builds + smoother HMR.
- Keep a single `index.html` template in Django to avoid duplicating the CRA/Vite `index.html`.
- Only expose **safe public config** via `window.__APP_CONFIG__`.

---

## Docker

- Production-like image builds the CRA app and serves Django via Gunicorn.
- Dev compose runs Django dev server and CRA dev server separately for HMR.

### Quick start (production-like)

```bash
# Build and run
docker compose up --build

# App is available at http://localhost:8000
```

- The image builds the React app, copies it into the container, and runs `collectstatic`.
- WhiteNoise serves static files; SQLite is used by default. Add a DB service if needed.

Environment variables:

- `DJANGO_ALLOWED_HOSTS` (default `*`)
- `DJANGO_DEBUG` (`0`/`1`, default `0`)
- `PORT` (default `8000`)
- `DEV_MODE`, `FRONTEND_DEV_SERVER_URL` are optional and mainly for dev/HMR setups.

### Development (with HMR)

```bash
docker compose -f docker-compose.dev.yml up

# Django: http://localhost:8000
# CRA dev server (HMR): http://localhost:3000
```

- In this mode, browse the CRA dev server on port 3000 for HMR.
- The CRA dev server does not use the Django template runtime config. If your UI calls the backend, configure your frontend to call `http://localhost:8000` for API requests (e.g., via env or a proxy in CRA).

