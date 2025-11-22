"""
Utility Library - Generation 0
This library evolves autonomously through Recursive Intelligence.
"""

import re
_EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validate an email address using compiled regex pattern."""
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_PATTERN.match(email))
def slugify(text):
    """Convert text to URL-friendly slug with unicode support."""
    import re
    import unicodedata
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace non-alphanumeric with dashes
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
    return slug.strip('-')

def truncate(text, length, suffix="..."):
    """Truncate text to specified length, respecting word boundaries."""
    if not text or len(text) <= length:
        return text

    # Find last space before length
    truncated = text[:length]
    last_space = truncated.rfind(' ')

    if last_space > length // 2:
        return truncated[:last_space] + suffix
    return truncated + suffix

def parse_int(value):
    """Parse a value to integer."""
    try:
        return int(value)
    except:
        return None


def unique(items):
    """Get unique items from list."""
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
