from markdown import markdown
import bleach

ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
    'ol', 'strong', 'ul', 'p', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'br', 'hr'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'abbr': ['title'],
    'acronym': ['title'],
}

def markdown_filter(text):
    raw_html = markdown(text or "")
    safe_html = bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return safe_html
