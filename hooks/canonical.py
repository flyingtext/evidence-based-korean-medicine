import gzip
import os
import re

SITE_URL = "https://wiki.symbolicinfo.com"

CANONICAL_RE = re.compile(r'<link[^>]+rel="canonical"[^>]*>')


def on_post_page(output, page, config):
    return CANONICAL_RE.sub(
        f'<link rel="canonical" href="{SITE_URL}/{page.url}">', output
    )


def _fix_sitemap(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("http://127.0.0.1:8000", SITE_URL)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    with gzip.open(f"{path}.gz", "wb") as gz_buf:
        gz_buf.write(content.encode("utf-8"))


def on_post_build(config):
    _fix_sitemap(os.path.join(config["site_dir"], "sitemap.xml"))
