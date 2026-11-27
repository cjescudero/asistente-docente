"""Translate the course map's trusted interface before inserting any course data."""
import html
import json
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _english_labels():
    labels = Path(__file__).resolve().parents[1] / "assets" / "map-en.json"
    return json.loads(labels.read_text(encoding="utf-8"))


def label(text, language):
    return _english_labels()[text] if language == "en" else text


def render_template(template, language):
    def substitute(match):
        context, source = match.groups()
        translated = label(source, language)
        if context == "text":
            return html.escape(translated, quote=True)
        return json.dumps(translated, ensure_ascii=False).replace("<", "\\u003c")

    template = template.replace("[[locale]]", html.escape(language, quote=True))
    return re.sub(r"\[\[(text|js):([^\]]+)\]\]", substitute, template)
