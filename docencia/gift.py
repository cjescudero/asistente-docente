"""Read an explicit, lossless subset of GIFT using only the standard library.

Supported: named choice, true/false, numerical and matching questions; categories,
four question text formats, escaped control characters and feedback. The grammar
is implemented here from Moodle's public GIFT format documentation, not from
Moodle's implementation. This is not a complete Moodle importer.

Deliberately rejected: unnamed/duplicate IDs, short answer, essay, descriptions,
Cloze, missing-word text after an answer block, nested/unescaped content braces,
per-answer format overrides, and unsupported or inconsistent answer weights.
Only whole lines starting with ``//`` are comments: URLs are never truncated.
Matching requires at least three pairs and has no per-pair weights or feedback.
Unknown backslash escapes are preserved; literal backslashes can be doubled.
"""

from __future__ import annotations

import math
import re
from typing import Any


class GiftError(ValueError):
    """A GIFT input cannot be represented without guessing or losing meaning."""


_ESCAPED = frozenset("\\~=#{}:")
_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")
_WEIGHT = re.compile(r"%([+-]?(?:\d+(?:\.\d*)?|\.\d+))%")
_FORMAT = re.compile(r"^\[([a-zA-Z]+)\]")
_FORMATS = {"html", "plain", "markdown", "moodle"}


def escape_gift(text: str) -> str:
    """Escape a text fragment, including literal backslashes and newlines.

    This function escapes content, not complete GIFT documents or category-path
    separators. Decode/encode preserves Unicode without replacing HTML entities.
    """
    if not isinstance(text, str):
        raise TypeError("El texto que se escapa debe ser una cadena.")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(
        "\\n" if char == "\n" else "\\" + char if char in _ESCAPED else char
        for char in text
    )


def _decode(text: str) -> str:
    output: list[str] = []
    pos = 0
    while pos < len(text):
        char = text[pos]
        if char == "\\" and pos + 1 < len(text):
            following = text[pos + 1]
            if following in _ESCAPED or following == "n":
                output.append("\n" if following == "n" else following)
                pos += 2
                continue
        output.append(char)
        pos += 1
    return "".join(output)


def _positions(text: str, token: str) -> list[int]:
    """Locate structural tokens, respecting odd/even escaped backslashes."""
    positions: list[int] = []
    pos = 0
    while pos < len(text):
        if (
            text[pos] == "\\"
            and pos + 1 < len(text)
            and (text[pos + 1] in _ESCAPED or text[pos + 1] == "n")
        ):
            pos += 2
            continue
        if text.startswith(token, pos):
            positions.append(pos)
            pos += len(token)
        else:
            pos += 1
    return positions


def _first(text: str, token: str, start: int = 0) -> int:
    found = _positions(text[start:], token)
    return start + found[0] if found else -1


def _split(text: str, token: str) -> list[str]:
    starts = _positions(text, token)
    result: list[str] = []
    last = 0
    for pos in starts:
        result.append(text[last:pos])
        last = pos + len(token)
    result.append(text[last:])
    return result


def _float(text: str, label: str) -> float:
    text = text.strip()
    if not _NUMBER.fullmatch(text):
        raise GiftError(f"{label}: se esperaba un número con punto decimal: {text!r}.")
    value = float(text)
    if not math.isfinite(value):
        raise GiftError(f"{label}: el valor debe ser finito.")
    return value


def _take_weight(text: str, default: float) -> tuple[float, str, bool]:
    text = text.strip()
    if not text.startswith("%"):
        return default, text, False
    match = _WEIGHT.match(text)
    if not match:
        raise GiftError("Peso inválido: usar %número% al comienzo de la respuesta.")
    weight = _float(match.group(1), "Peso")
    if not -100 <= weight <= 100:
        raise GiftError("El peso debe estar entre -100 y 100 por ciento.")
    return weight, text[match.end() :].strip(), True


def _text_feedback(text: str) -> tuple[str, str]:
    parts = _split(text, "#")
    if len(parts) > 2:
        raise GiftError("Varios marcadores de feedback; escapar los # literales.")
    answer = parts[0].strip()
    format_match = _FORMAT.match(answer)
    if format_match and format_match.group(1).lower() in _FORMATS:
        raise GiftError("Los formatos específicos por respuesta no están soportados.")
    return _decode(answer), _decode(parts[1].strip()) if len(parts) == 2 else ""


def _items(body: str, allowed: str) -> list[tuple[str, str]]:
    markers = sorted((pos, marker) for marker in allowed for pos in _positions(body, marker))
    if not markers or body[: markers[0][0]].strip():
        raise GiftError("Las respuestas deben empezar por = o ~, según su tipo.")
    result = []
    for index, (pos, marker) in enumerate(markers):
        end = markers[index + 1][0] if index + 1 < len(markers) else len(body)
        result.append((marker, body[pos + 1 : end].strip()))
    return result


def _truefalse(body: str) -> dict[str, Any] | None:
    parts = _split(body, "#")
    token = parts[0].strip().upper()
    if token not in {"T", "F", "TRUE", "FALSE"}:
        return None
    if len(parts) > 3:
        raise GiftError("Verdadero/falso admite como máximo feedback erróneo y correcto.")
    answer = token in {"T", "TRUE"}
    result: dict[str, Any] = {"type": "truefalse", "true_answer": answer}
    if len(parts) > 1:
        wrong_feedback = _decode(parts[1].strip())
        right_feedback = _decode(parts[2].strip()) if len(parts) == 3 else ""
        result["options"] = [
            {
                "text": label,
                "weight": 100.0 if truth == answer else 0.0,
                "feedback": right_feedback if truth == answer else wrong_feedback,
            }
            for truth, label in ((True, "Verdadero"), (False, "Falso"))
        ]
    return result


def _numerical(body: str) -> dict[str, Any]:
    body = body[1:].strip()
    if not body:
        raise GiftError("La pregunta numérica no contiene respuestas.")
    if _positions(body, "~"):
        raise GiftError("Las respuestas numéricas se separan con =, no con ~.")
    if body.startswith("="):
        entries = [text for _, text in _items(body, "=")]
    else:
        if _positions(body, "="):
            raise GiftError("En numéricas múltiples, todas las respuestas deben empezar por =.")
        if body.startswith("%"):
            raise GiftError("Una respuesta numérica ponderada debe empezar por =%peso%.")
        entries = [body]
    answers: list[dict[str, Any]] = []
    for entry in entries:
        weight, text, _ = _take_weight(entry, 100.0)
        value_text, feedback = _text_feedback(text)
        answer: dict[str, Any] = {"weight": weight, "feedback": feedback}
        if ".." in value_text:
            bounds = value_text.split("..")
            if len(bounds) != 2 or ":" in value_text:
                raise GiftError("Intervalo numérico inválido; usar mínimo..máximo.")
            low = _float(bounds[0], "Mínimo")
            high = _float(bounds[1], "Máximo")
            if low > high:
                raise GiftError("El mínimo del intervalo supera al máximo.")
            answer.update(min=low, max=high)
        else:
            parts = value_text.split(":")
            if len(parts) > 2:
                raise GiftError("Respuesta numérica inválida; usar valor:tolerancia.")
            value = _float(parts[0], "Valor numérico")
            tolerance = _float(parts[1], "Tolerancia") if len(parts) == 2 else 0.0
            if tolerance < 0:
                raise GiftError("La tolerancia no puede ser negativa.")
            if not math.isfinite(value - tolerance) or not math.isfinite(value + tolerance):
                raise GiftError("Los límites de la tolerancia deben ser finitos.")
            answer.update(value=value, tolerance=tolerance)
        answers.append(answer)
    if not any(answer["weight"] == 100.0 for answer in answers):
        raise GiftError("La pregunta numérica necesita una respuesta con crédito completo.")
    return {"type": "numerical", "numerical": answers}


def _matching(entries: list[tuple[str, str]]) -> dict[str, Any]:
    if len(entries) < 3:
        raise GiftError("El emparejamiento requiere al menos tres pares.")
    matches: list[dict[str, str]] = []
    seen: set[str] = set()
    for marker, entry in entries:
        if marker != "=" or entry.startswith("%") or _positions(entry, "#"):
            raise GiftError("Emparejamiento no admite ~, pesos ni feedback por pareja.")
        parts = _split(entry, "->")
        if len(parts) != 2:
            raise GiftError("Cada pareja debe contener exactamente un separador ->.")
        left, right = (_decode(part.strip()) for part in parts)
        if not left or not right:
            raise GiftError("Los dos elementos de cada pareja deben tener texto.")
        if left in seen:
            raise GiftError("Los enunciados de las parejas de emparejamiento deben ser únicos.")
        seen.add(left)
        matches.append({"left": left, "right": right})
    return {"type": "matching", "matches": matches}


def _choice(body: str) -> dict[str, Any]:
    entries = _items(body, "=~")
    has_tilde = any(marker == "~" for marker, _ in entries)
    has_arrow = any(_positions(entry, "->") for _, entry in entries)
    if has_arrow and not has_tilde:
        return _matching(entries)
    if not has_tilde:
        raise GiftError("Respuesta corta no soportada: todas las respuestas empiezan por =.")
    equals = sum(marker == "=" for marker, _ in entries)
    if equals > 1:
        raise GiftError("Selección única con varias respuestas =; usar ~%peso% para selección múltiple.")
    question_type = "single" if equals else "multiple"
    options: list[dict[str, Any]] = []
    seen: set[str] = set()
    for marker, entry in entries:
        weight, raw_text, _ = _take_weight(entry, 100.0 if marker == "=" else 0.0)
        if marker == "=" and weight != 100.0:
            raise GiftError("En selección única, la opción = debe valer el 100 por ciento.")
        text, feedback = _text_feedback(raw_text)
        if not text:
            raise GiftError("Una opción no puede estar vacía.")
        if text in seen:
            raise GiftError("Hay opciones con el mismo texto; no se puede distinguir la respuesta.")
        seen.add(text)
        options.append({"text": text, "weight": weight, "feedback": feedback})
    if len(options) < 2:
        raise GiftError("La selección requiere al menos dos opciones.")
    if question_type == "multiple":
        positive_sum = math.fsum(option["weight"] for option in options if option["weight"] > 0)
        if not math.isclose(positive_sum, 100.0, rel_tol=0, abs_tol=0.001):
            raise GiftError("Los pesos positivos de selección múltiple deben sumar 100 por ciento.")
    elif any(marker == "~" and option["weight"] == 100 for (marker, _), option in zip(entries, options)):
        raise GiftError("Selección única contiene más de una respuesta con crédito completo.")
    return {"type": question_type, "options": options}


def _body(body: str) -> dict[str, Any]:
    general = _split(body, "####")
    if len(general) > 2:
        raise GiftError("La pregunta contiene varios bloques de feedback general.")
    body = general[0].strip()
    if not body:
        raise GiftError("Ensayo o bloque de respuestas vacío no soportado.")
    truefalse = _truefalse(body)
    if truefalse is not None:
        result = truefalse
    elif body.startswith("#"):
        result = _numerical(body)
    elif body.startswith(("=", "~")):
        result = _choice(body)
    else:
        raise GiftError("Tipo no soportado o bloque mal formado (respuesta corta, Cloze o llave de contenido sin escapar).")
    if len(general) == 2:
        result["feedback"] = _decode(general[1].strip())
    return result


def parse_gift(text: str) -> list[dict[str, Any]]:
    """Parse a GIFT string to the JSON-compatible question contract.

    Titles are required stable IDs, unique throughout the bank. Category paths
    are unrestricted and default to an empty string until a $CATEGORY directive.
    Text after ``}`` is rejected rather than silently changing a missing-word
    question. Errors include the question ID or source line where possible.
    """
    if not isinstance(text, str):
        raise TypeError("parse_gift necesita el contenido GIFT como cadena, no una ruta.")
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join("" if line.lstrip().startswith("//") else line for line in text.split("\n"))
    questions: list[dict[str, Any]] = []
    ids: set[str] = set()
    category = ""
    pos = 0
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos == len(text):
            break
        line = text.count("\n", 0, pos) + 1
        if text.startswith("$CATEGORY:", pos):
            end = text.find("\n", pos)
            end = len(text) if end == -1 else end
            category = _decode(text[pos + len("$CATEGORY:") : end].strip())
            if not category:
                raise GiftError(f"Línea {line}: la categoría está vacía.")
            pos = end
            continue
        if not text.startswith("::", pos):
            raise GiftError(f"Línea {line}: se requiere ::identificador::; no se admite texto después de }} ni preguntas sin título.")
        title_end = _first(text, "::", pos + 2)
        if title_end == -1:
            raise GiftError(f"Línea {line}: falta cerrar el identificador con ::.")
        question_id = _decode(text[pos + 2 : title_end].strip())
        if not question_id or "\n" in question_id:
            raise GiftError(f"Línea {line}: el identificador debe ser no vacío y de una sola línea.")
        if question_id in ids:
            raise GiftError(f"Identificador GIFT duplicado: {question_id!r}.")
        prompt_start = title_end + 2
        answer_start = _first(text, "{", prompt_start)
        next_title = _first(text, "::", prompt_start)
        stray_close = _first(text, "}", prompt_start)
        if answer_start == -1 or (next_title != -1 and next_title < answer_start):
            raise GiftError(f"Pregunta {question_id!r}: falta el bloque de respuestas.")
        if stray_close != -1 and stray_close < answer_start:
            raise GiftError(f"Pregunta {question_id!r}: llave de cierre sin escapar en el enunciado.")
        answer_end = _first(text, "}", answer_start + 1)
        nested = _first(text, "{", answer_start + 1)
        if answer_end == -1:
            raise GiftError(f"Pregunta {question_id!r}: falta cerrar el bloque de respuestas.")
        if nested != -1 and nested < answer_end:
            raise GiftError(f"Pregunta {question_id!r}: llaves anidadas; escapar las llaves de TeX/contenido. Cloze no está soportado.")
        raw_prompt = text[prompt_start:answer_start].strip()
        if re.search(r"(?:\\(?:frac|dfrac|tfrac|sqrt|text|textrm|textbf|mathrm|mathbf|mathit|operatorname|overline|underline|underbrace|overbrace|begin|end)(?:\[[^\]\n]*\])?|[_^])\s*$", raw_prompt):
            raise GiftError(f"Pregunta {question_id!r}: una llave de TeX debe escaparse; no se interpreta como bloque de respuestas.")
        question_format = "moodle"
        format_match = _FORMAT.match(raw_prompt)
        if format_match:
            question_format = format_match.group(1).lower()
            if question_format not in _FORMATS:
                raise GiftError(f"Pregunta {question_id!r}: formato {question_format!r} no soportado.")
            raw_prompt = raw_prompt[format_match.end() :].strip()
        if not raw_prompt:
            raise GiftError(f"Pregunta {question_id!r}: el enunciado está vacío.")
        try:
            parsed = _body(text[answer_start + 1 : answer_end])
        except GiftError as error:
            raise GiftError(f"Pregunta {question_id!r}: {error}") from error
        questions.append({
            "id": question_id,
            "category": category,
            "prompt": _decode(raw_prompt),
            "format": question_format,
            **parsed,
        })
        ids.add(question_id)
        pos = answer_end + 1
    return questions
