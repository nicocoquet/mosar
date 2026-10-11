"""Lightweight static checks for Mosar Admin FR/EN pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for page in ('admin.md', 'admin.en.md'):
    source = (ROOT / 'docs' / page).read_text(encoding='utf-8')
    assert '# Admin' in source, page
    assert 'id="mosar-admin"' in source, page
    assert 'data-api-url=""' in source, page  # fail closed before Render setup
    assert 'id="admin-publish"' in source, page
js = (ROOT / 'docs/javascripts/admin.js').read_text(encoding='utf-8')
for endpoint in ('/auth/github', '/auth/session', '/api/preview', '/api/publish', '/api/jobs/'):
    assert endpoint in js, endpoint
assert 'localStorage' not in js and 'sessionStorage' not in js
print('Pages Admin FR/EN : OK')
