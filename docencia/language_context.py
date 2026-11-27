"""Scope the language of diagnostic text to a single synchronous or concurrent task."""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps


_language = ContextVar("teaching_assistant_language", default="es")


def current_language():
    return _language.get()


@contextmanager
def use_language(language):
    if language not in ("en", "es"):
        raise ValueError("Supported languages: en, es / Idiomas disponibles: en, es.")
    token = _language.set(language)
    try:
        yield
    finally:
        _language.reset(token)


def with_diagnostics(function):
    @wraps(function)
    def localized(*args, **kwargs):
        with use_language(kwargs.get("language") or current_language()):
            return function(*args, **kwargs)
    return localized
