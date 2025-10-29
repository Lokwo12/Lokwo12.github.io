from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def absolute_static(context, path: str) -> str:
    """
    Build an absolute URL for a static asset using the current request.
    Falls back to relative static URL if request is missing.
    Usage: {% absolute_static 'images/og-default.svg' %}
    """
    try:
        url = static(path)
    except Exception:
        url = path
    request = context.get('request')
    if request:
        try:
            return request.build_absolute_uri(url)
        except Exception:
            return url
    return url

@register.simple_tag(takes_context=True)
def absolute_url(context, url_path: str) -> str:
    """
    Convert a relative/media URL into an absolute URL using the current request.
    Usage: {% absolute_url obj.image.url %}
    """
    if not url_path:
        return ''
    request = context.get('request')
    if request:
        try:
            return request.build_absolute_uri(url_path)
        except Exception:
            return url_path
    return url_path


def _tech_badge_svg(label: str, size: int = 18, color_a: str = "#6366f1", color_b: str = "#60a5fa") -> str:
    label = (label or "").strip()[:3]
    svg = f'''
    <svg class="tech-svg" width="{size}" height="{size}" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{color_a}"/>
          <stop offset="100%" stop-color="{color_b}"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#g)"/>
    <text x="12" y="15" text-anchor="middle" font-size="10" font-weight="700" font-family="system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif" fill="#fff">{label}</text>
    </svg>
    '''
    return svg


@register.simple_tag
def tech_icon(name: str, size: int = 18) -> str:
    """Return a small inline SVG badge for a technology name.
    Known tech get nice color pairs and short codes; others use initials.
    Usage: {% tech_icon 'Python' 18 %}
    """
    if not name:
        return ''
    key = str(name).strip().lower()
    mapping = {
        'python':        ("Py", "#3776AB", "#4B8BBE"),
        'django':        ("Dj", "#092E20", "#2E8B57"),
        'react':         ("Re", "#61DAFB", "#3FA8C9"),
        'javascript':    ("JS", "#F7DF1E", "#EAB308"),
        'typescript':    ("TS", "#3178C6", "#2563EB"),
        'html':          ("HT", "#E34F26", "#F97316"),
        'css':           ("CS", "#1572B6", "#38BDF8"),
        'postgres':      ("PG", "#336791", "#3B82F6"),
        'postgresql':    ("PG", "#336791", "#3B82F6"),
        'sqlite':        ("SQ", "#0F80CC", "#38BDF8"),
        'docker':        ("Do", "#0DB7ED", "#0891B2"),
        'git':           ("Gt", "#F1502F", "#F97316"),
        'github':        ("Gh", "#1F2937", "#6B7280"),
        'linkedin':      ("In", "#0A66C2", "#0E7490"),
        'twitter':       ("Tw", "#1DA1F2", "#0284C7"),
        'youtube':       ("Yt", "#FF0000", "#DC2626"),
        'node':          ("Nd", "#3C873A", "#16A34A"),
        'node.js':       ("Nd", "#3C873A", "#16A34A"),
        'next':          ("Nx", "#111827", "#4B5563"),
        'next.js':       ("Nx", "#111827", "#4B5563"),
        'bootstrap':     ("Bs", "#7952B3", "#6D28D9"),
        'tailwind':      ("Tw", "#06B6D4", "#60A5FA"),
        'whitenoise':    ("WN", "#0EA5E9", "#22D3EE"),
    }
    if key in mapping:
        code, a, b = mapping[key]
    else:
        # Build initials from words, fallback to first 2 chars
        parts = [p for p in key.replace('.', ' ').split() if p]
        if len(parts) >= 2:
            code = (parts[0][0] + parts[1][0]).upper()
        else:
            code = key[:2].upper()
        a, b = "#6366f1", "#60a5fa"

    svg = _tech_badge_svg(code, size=size, color_a=a, color_b=b)
    return mark_safe(svg)


@register.filter
def bullet_lines(text: str):
    """Split text into bullet lines by newlines or semicolons or • markers.
    Returns a list of trimmed non-empty lines.
    Usage: {% for line in job.summary|bullet_lines %}<li>{{ line }}</li>{% endfor %}
    """
    if not text:
        return []
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return []
    import re
    parts = re.split(r"\n+|\u2022+|;+", text)
    return [p.strip() for p in parts if p and p.strip()]


@register.simple_tag
def merge_lists(a=None, b=None, limit: int = None):
    """Merge two list-like values, de-duplicate while preserving order, and optionally limit length.
    Usage:
      {% merge_lists PROFILE.skills PROFILE.tools 6 as core_skills %}
    """
    result = []
    def as_list(x):
        if not x:
            return []
        if isinstance(x, (list, tuple)):
            return list(x)
        # Strings are split by comma
        if isinstance(x, str):
            return [i.strip() for i in x.split(',') if i.strip()]
        return []
    for item in as_list(a) + as_list(b):
        if item not in result:
            result.append(item)
    try:
        if limit is not None:
            limit_int = int(limit)
            result = result[:max(0, limit_int)]
    except Exception:
        pass
    return result


@register.filter(name="get")
def get_item(obj, key):
    """Safely get a key/attr from a dict or object in templates.
    Usage: {{ some_dict|get:'key' }} — returns None if missing instead of raising.
    Also works for simple attribute access on objects.
    """
    try:
        if obj is None or key is None:
            return None
        if isinstance(obj, dict):
            return obj.get(key)
        # Fallback to attribute access
        return getattr(obj, str(key), None)
    except Exception:
        return None



