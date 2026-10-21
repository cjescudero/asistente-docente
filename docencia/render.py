"""HTML autocontenido e impresión; no ejecuta HTML activo del material fuente."""

from __future__ import annotations

import html
import os
import re
from html.parser import HTMLParser
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MATHJAX = PACKAGE_ROOT / "assets/vendor/mathjax/tex-svg.js"
CSS = """
@page { size: A4; margin: 19mm 18mm 20mm; }
* { box-sizing: border-box; }
body { font: 11pt/1.52 Georgia, 'Times New Roman', serif; color:#182127;
       margin:0 auto; max-width:174mm; background:white; }
h1,h2,h3,.eyebrow,.meta { font-family:Arial,sans-serif; }
h1 { font-size:24pt; line-height:1.2; margin:8px 0 12px; }
h2 { font-size:14pt; margin:24px 0 8px; }
.eyebrow { font-size:9pt; letter-spacing:1.6px; color:#476069; }
.meta { font-size:10pt; border-bottom:2px solid #244c57; padding:0 0 12px; }
 .questionnaire { font:10.5pt/1.35 Arial,sans-serif; }
.questionnaire-header { display:flex; align-items:baseline; justify-content:space-between; gap:20px; }
.questionnaire-header h1 { font-size:19pt; margin:0 0 12px; }
.model-id { font-weight:bold; white-space:nowrap; color:#244c57; }
.identity-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; font-size:9pt; font-weight:bold; color:#244c57; }
.identity-grid span { display:block; height:25px; border-bottom:1px solid #476069; }
.instructions { border-bottom:1px solid #244c57; padding:9px 0 11px; margin-bottom:18px; font-size:9pt; color:#3f4e54; }
.scoring { font:8.5pt/1.35 Arial,sans-serif; color:#3f4e54; margin:6px 0; }
.question-heading { display:flex; justify-content:space-between; align-items:baseline; gap:12px; color:#244c57; }
.question-heading span { font: bold 8pt Arial,sans-serif; letter-spacing:.3px; }
.questionnaire .options { padding:0; }
.questionnaire .options li { display:flex; gap:8px; align-items:baseline; margin:4px 0; }
.questionnaire .options li p { margin:0; }
.questionnaire .label { border:1px solid #244c57; width:18px; min-width:18px; height:18px; text-align:center; font: bold 9pt/16px Arial,sans-serif; color:#244c57; }
.circle .label { border-radius:50%; }
.square .label { border-radius:2px; }
.identity { margin:18px 0 24px; color:#3f4e54; }
.question { break-inside:avoid; margin:20px 0; }
.question h2 { font-size:11.5pt; margin:0 0 6px; }
.options { list-style:none; padding:0 0 0 8px; margin:8px 0; }
.options li { margin:5px 0; }
.label { display:inline-block; min-width:25px; font-weight:bold; }
.answer { border-left:3px solid #628178; padding:8px 12px; background:#f2f6f4; }
.numeric { margin:16px 0; }
table { border-collapse:collapse; width:100%; margin:12px 0; }
td,th { border:1px solid #adb7bb; padding:7px; text-align:left; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; padding:10px; background:#f4f5f6; }
code { font:9pt/1.45 monospace; }
img,svg { max-width:100%; }
p { margin:7px 0; }
blockquote { border-left:2px solid #aaa; margin-left:0; padding-left:14px; }
@media screen { body { padding:28px; } }
"""


def external_output(path: str | Path) -> Path:
    """Los datos del profesor no deben guardarse en el plugin instalado."""
    target = Path(path).expanduser().resolve()
    if target == PACKAGE_ROOT or PACKAGE_ROOT in target.parents:
        raise ValueError("El directorio de resultados debe estar fuera del paquete del plugin.")
    return target


class SafeHTML(HTMLParser):
    TAGS = {"p", "br", "strong", "b", "em", "i", "u", "sub", "sup", "code",
            "pre", "ul", "ol", "li", "table", "thead", "tbody", "tr", "td",
            "th", "blockquote", "h1", "h2", "h3", "h4", "hr", "span", "div"}
    VOID = {"br", "hr"}
    DROP = {"script", "style", "iframe", "object", "embed", "svg", "math"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.stack = []
        self.drop = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.DROP:
            raise ValueError(f"HTML no soportado: <{tag}>. Adapta el contenido antes de imprimir.")
        if tag == "img":
            raise ValueError("Las imágenes HTML requieren adaptación explícita; no se omiten silenciosamente.")
        if tag in self.TAGS:
            structural = ""
            for key, value in attrs:
                if key in {"rowspan", "colspan"} and tag in {"td", "th"}:
                    if not value or not value.isdecimal() or not 1 <= int(value) <= 100:
                        raise ValueError(f"Atributo de tabla no válido: {key}.")
                    structural += f' {key}="{int(value)}"'
                elif key.lower().startswith("on"):
                    raise ValueError("HTML activo no permitido en un documento imprimible.")
            self.parts.append(f"<{tag}{structural}>")
            if tag not in self.VOID:
                self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.drop:
            if tag in self.DROP:
                self.drop -= 1
            return
        if tag in self.stack:
            while self.stack:
                current = self.stack.pop()
                self.parts.append(f"</{current}>")
                if current == tag:
                    break

    def handle_data(self, data):
        if not self.drop:
            self.parts.append(html.escape(data, quote=False))

    def result(self):
        return "".join(self.parts) + "".join(f"</{t}>" for t in reversed(self.stack))


def fragment(text: str, fmt: str = "html") -> str:
    if fmt == "markdown":
        try:
            from markdown_it import MarkdownIt
        except ImportError as exc:
            raise RuntimeError("Falta markdown-it-py; instala requirements.txt.") from exc
        saved = []

        def protect(match):
            saved.append(match.group())
            return f"MATHPLACEHOLDER{len(saved)-1}END"

        protected = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", protect, text, flags=re.S)
        text = MarkdownIt("commonmark", {"html": False}).enable("table").render(protected)
        for i, math in enumerate(saved):
            text = text.replace(f"MATHPLACEHOLDER{i}END", html.escape(math))
    elif fmt == "plain":
        return html.escape(text).replace("\n", "<br>")
    elif fmt == "moodle":
        # Autoformato habitual GIFT: conservar HTML básico y saltos de línea.
        text = text.replace("\n", "<br>")
    sanitizer = SafeHTML()
    sanitizer.feed(text)
    sanitizer.close()
    return sanitizer.result()


def document(title: str, body: str, *, math: bool = False) -> str:
    script = ""
    if math:
        if not MATHJAX.is_file():
            raise RuntimeError("Falta el recurso MathJax empaquetado.")
        # La configuración y el JS son recursos del paquete, nunca del banco.
        config = r"""window.MathJax={loader:{load:[]},tex:{inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']],packages:['base','ams','newcommand']},svg:{fontCache:'local'},options:{enableMenu:false}};"""
        js = MATHJAX.read_text(encoding="utf-8").replace("</script", "<\\/script")
        script = f"<script>{config}</script><script>{js}</script>"
    return ("<!doctype html><html lang='es'><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body>{body}{script}</body></html>")


def print_pdf(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    """Un fallo conserva el HTML; no registra un PDF inexistente como generado."""
    browser = None
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            override = os.environ.get("ASISTENTE_DOCENTE_CHROMIUM")
            browser = playwright.chromium.launch(headless=True, executable_path=override or None)
            page = browser.new_page()
            page.route("**/*", lambda route: route.abort())
            page.set_content(html_path.read_text(encoding="utf-8"), wait_until="load")
            page.evaluate("async () => { if(window.MathJax?.startup) await MathJax.startup.promise; await document.fonts.ready; }")
            if page.locator("mjx-merror, [data-mjx-error]").count():
                raise ValueError("MathJax detectó una fórmula no válida.")
            page.pdf(path=str(pdf_path), format="A4", print_background=True,
                     prefer_css_page_size=True, display_header_footer=True,
                     header_template="<span></span>",
                     footer_template="<div style='width:100%;text-align:center;font-size:9px;color:#666'><span class='pageNumber'></span> / <span class='totalPages'></span></div>")
            browser.close()
        return True, "generated"
    except Exception as exc:
        pdf_path.unlink(missing_ok=True)
        reason = str(exc).splitlines()[0][:350]
        return False, f"PDF pendiente: {type(exc).__name__}: {reason}"


def render_markdown(source: str | Path, output: str | Path, *, title: str | None = None,
                    html_only: bool = False) -> dict:
    source = Path(source).resolve()
    output = external_output(output)
    text = source.read_text(encoding="utf-8")
    rendered = fragment(text, "markdown")
    page = document(title or source.stem, rendered, math="\\(" in text or "\\[" in text)
    output.mkdir(parents=True, exist_ok=True)
    html_path = output / f"{source.stem}.html"
    pdf_path = output / f"{source.stem}.pdf"
    if html_path.exists() or pdf_path.exists():
        raise ValueError("Ya existen resultados con ese nombre; elige otra carpeta.")
    html_path.write_text(page, encoding="utf-8")
    ok, status = (False, "not_requested") if html_only else print_pdf(html_path, pdf_path)
    return {"html": str(html_path), "pdf": str(pdf_path) if ok else None, "pdf_status": status}
