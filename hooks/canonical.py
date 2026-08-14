import re

SITE_URL = "https://wiki.symbolicinfo.com"

CANONICAL_RE = re.compile(r'<link[^>]+rel="canonical"[^>]*>')


def on_post_page(output, page, config):
    return CANONICAL_RE.sub(
        f'<link rel="canonical" href="{SITE_URL}/{page.url}">', output
    )
