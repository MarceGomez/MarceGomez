"""Descarga una sola vez los paths de los logos (Simple Icons) a scripts/icons.json.

Uso: python scripts/fetch_icons.py
Algunos logos (Microsoft, Adobe, AWS) se retiraron de versiones recientes, por eso se prueba en varias versiones fijas.
"""
import json
import re
import urllib.request
from pathlib import Path

SLUGS = [
    "claude", "anthropic", "openai", "googlegemini", "elevenlabs", "modelcontextprotocol",
    "python", "typescript", "javascript", "html5", "sass",
    "django", "nestjs", "nodedotjs", "vuedotjs", "symfony", "bootstrap",
    "amazonwebservices", "amazonaws", "microsoftazure", "cloudflare",
    "azuredevops", "githubactions", "git", "github", "nginx", "visualstudiocode",
    "postgresql", "mysql", "postman", "swagger", "jira", "confluence", "trello",
    "figma", "adobeillustrator", "sketch",
]
VERSIONS = ["15.16.0", "13.21.0", "11.15.0", "9.21.0"]
OUT = Path(__file__).with_name("icons.json")

icons = {}
for slug in SLUGS:
    for v in VERSIONS:
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@{v}/icons/{slug}.svg"
        try:
            svg = urllib.request.urlopen(url, timeout=20).read().decode()
        except Exception:
            continue
        m = re.search(r'<path d="([MmLlHhVvCcSsQqTtAaZz0-9.,\s-]+)"', svg)
        if m:
            icons[slug] = m.group(1)
            print(f"{slug:22} v{v}")
            break
    else:
        print(f"{slug:22} NO ENCONTRADO")

OUT.write_text(json.dumps(icons, indent=1), encoding="utf-8")
