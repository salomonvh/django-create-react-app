# mkdir -p backend/core/templatetags && touch __init__.py
import json
from pathlib import Path
from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

def _manifest():
    # read directly from frontend/build (not via staticfiles)
    project_root = getattr(settings, "PROJECT_ROOT", settings.BASE_DIR.parent)
    mf = project_root / "frontend" / "build" / "asset-manifest.json"
    return json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}

def _to_static_path(p: str) -> str:
    # "/static/css/main.hash.css" → "css/main.hash.css"
    # "static/css/main.hash.css"  → "css/main.hash.css"
    if p.startswith("/"):
        p = p[1:]
    if p.startswith("static/"):
        p = p[len("static/"):]
    return p

@register.simple_tag
def cra_css_tags():
    m = _manifest()
    tags = []
    files = m.get("files", {})
    for k, v in files.items():
        if k.endswith(".css"):
            logical = _to_static_path(v)
            tags.append(f'<link rel="stylesheet" href="{static(logical)}">')
    return mark_safe("\n".join(tags))

@register.simple_tag
def cra_js_tags():
    m = _manifest()
    tags = []
    # Prefer ordered "entrypoints" if present
    entrypoints = m.get("entrypoints") or []
    if entrypoints:
        for ep in entrypoints:
            if ep.endswith(".js"):
                logical = ep.lstrip("static/")
                tags.append(f'<script src="{static(logical)}"></script>')
    else:
        # common CRA chunks
        for key in ("runtime-main", "vendors", "2", "main"):
            for k, v in (m.get("files") or {}).items():
                if k.endswith(".js") and key in k:
                    logical = v.lstrip("/static/")
                    tags.append(f'<script src="{static(logical)}"></script>')
    return mark_safe("\n".join(tags))