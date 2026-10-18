"""Build assets/stack-{dark,light}.svg: the skillicons strip plus tiles skillicons doesn't have.

Edit ICONS / EXTRA below, then from the repo root:
    python3 assets/make_stack.py
"""
import re, urllib.request

ICONS = ("python,typescript,javascript,rust,dart,cpp,nodejs,bun,react,nextjs,tailwind,fastapi,django,"
         "flutter,postgres,prisma,redis,mongodb,docker,terraform,githubactions,aws,cloudflare,linux")
# lobehub icon name -> logo size inside the 256px tile (Codex's mark only fills 18 of its 24 units)
EXTRA = {"claude-color": 176, "codex-color": 216}
PERLINE = 13
LOBE = "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.95.1/icons/{}.svg"
TILE = {"dark": "#242938", "light": "#F4F2ED"}  # skillicons' own tile colours
CELL = 300  # skillicons: 256px tile + 44px gap


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "make_stack"})).read().decode()


def tile(name, size, index, theme):
    logo = get(LOBE.format(name))
    inner = re.search(r"<svg[^>]*>(.*)</svg>", logo, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner)
    inner = re.sub(r'<path d="[^"]*" fill="#fff"></path>', "", inner)  # codex-color's white backdrop; our tile replaces it
    x, y, pad = index % PERLINE * CELL, index // PERLINE * CELL, (256 - size) / 2
    return (f'<g transform="translate({x}, {y})"><title>{name.removesuffix("-color").title()}</title>'
            f'<rect width="256" height="256" fill="{TILE[theme]}" rx="60"/>'
            f'<svg x="{pad}" y="{pad}" width="{size}" height="{size}" viewBox="0 0 24 24">{inner}</svg></g>')


total = len(ICONS.split(",")) + len(EXTRA)
rows = -(-total // PERLINE)
for theme in TILE:
    svg = get(f"https://skillicons.dev/icons?i={ICONS}&perline={PERLINE}&theme={theme}")
    w, h = PERLINE * CELL - 44, rows * CELL - 44
    svg = re.sub(r'<svg width="[^"]+" height="[^"]+" viewBox="[^"]+"',
                 f'<svg width="{w * 48 / 256:g}" height="{h * 48 / 256:g}" viewBox="0 0 {w} {h}"', svg, count=1)
    extra = "".join(tile(n, s, len(ICONS.split(",")) + i, theme) for i, (n, s) in enumerate(EXTRA.items()))
    svg = svg[: svg.rindex("</svg>")] + extra + "</svg>\n"
    assert svg.count("<rect") >= total, f"{theme}: expected {total} tiles"
    open(f"assets/stack-{theme}.svg", "w").write(svg)
    print(f"assets/stack-{theme}.svg: {total} icons, {len(svg) / 1024:.0f} KB")
