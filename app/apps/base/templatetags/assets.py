import os
import re
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()

RESPONSIVE_WIDTHS = (480, 800, 1200)


def _static_path(path):
    """Путь к файлу статики: в DEBUG ищем в исходниках, в проде — в STATIC_ROOT."""
    found = finders.find(path)
    if found:
        return found
    candidate = os.path.join(settings.STATIC_ROOT, path)
    return candidate if os.path.exists(candidate) else None


def _minify_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,>])\s*', r'\1', css)
    css = css.replace(': ', ':').replace(';}', '}')
    return css.strip()


@lru_cache(maxsize=None)
def _read_css(path, mtime):
    with open(_static_path(path), encoding='utf-8') as fh:
        return _minify_css(fh.read())


@register.simple_tag
def inline_css(path):
    """Встраивает CSS прямо в HTML: не блокирует отрисовку отдельным запросом."""
    file_path = _static_path(path)
    if not file_path:
        return ''
    return mark_safe(_read_css(path, os.path.getmtime(file_path)))


@lru_cache(maxsize=None)
def _srcset_for(url):
    static_url = settings.STATIC_URL
    if not url.startswith(static_url) or not url.endswith('.webp'):
        return ''
    rel = url[len(static_url):]
    stem = rel[:-len('.webp')]
    parts = []
    for width in RESPONSIVE_WIDTHS:
        variant = f'{stem}-{width}.webp'
        if _static_path(variant):
            parts.append(f'{static_url}{variant} {width}w')
    if not parts:
        return ''
    original = _static_path(rel)
    if original:
        from PIL import Image
        with Image.open(original) as im:
            parts.append(f'{url} {im.width}w')
    return ', '.join(parts)


@register.filter
def srcset(url):
    """Для статичной .webp-картинки — набор уменьшенных копий для srcset."""
    return _srcset_for(str(url))


@register.simple_tag
def static_srcset(path):
    from django.templatetags.static import static
    return _srcset_for(static(path))


@register.filter
def ld_json(data):
    """Словарь → JSON для <script type="application/ld+json"> (с защитой от </script>)."""
    import json
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return mark_safe(raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))
