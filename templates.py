"""
Shared HTML/CSS constants used by both build_html.py and build_stats.py.
Change design tokens here and they propagate to both pages.
"""

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@700;800'
    "&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700"
    "&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600"
    '&display=swap" rel="stylesheet">'
)

BASE_CSS = """\
  :root {
    --bg: #16151a;
    --bg-raised: #201e25;
    --card: #221f27;
    --line: #34313b;
    --ink: #ece7da;
    --ink-muted: #938d80;
    --gold: #c9a34e;
    --rust: #b1503f;
    --teal: #4f8079;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
  }"""
