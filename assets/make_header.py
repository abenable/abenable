"""Generate assets/header.svg for the GitHub profile: terminal card + typed taglines + agent log panel.

Edit NAME / TAGS / META below, then from the repo root:
    uv run --with fonttools --with brotli assets/make_header.py assets/header.svg
Needs Fira Code installed (apt install fonts-firacode).
"""
import base64, io, sys
from fontTools import subset
from fontTools.ttLib import TTFont

OUT = sys.argv[1]
FONT = "/usr/share/fonts/truetype/firacode/FiraCode-{}.ttf"
ADV = 1200 / 1950  # Fira Code advance width in em, every glyph

W, H = 1200, 300
CYAN, INK, SOFT, MUTED, LINE, GREEN = "#22D3EE", "#F1F5F9", "#CBD5E1", "#64748B", "#1E293B", "#4ADE80"

NAME = "Able Abenaitwe"
PROMPT = [("able@github", CYAN), (":~$ ", MUTED), ("whoami", SOFT)]
TAGS = [
    "I build AI agents that do real work.",
    "I ship full-stack apps, front to back.",
    "I keep the servers up. Mostly.",
    "I study EE at Makerere University.",
]
META = "Software Engineer @ Feyti Medical Group · Junior Infra Manager @ Marconi"
# right-hand panel: an ops-agent session diagnosing a crash with read-only tools, the way ops-agent works
AGENT_TITLE = "ops-agent · #infra"
AGENT = [
    [("you  ", MUTED), ("why is loki down?", INK)],
    [("tool ", MUTED), ("docker_status", CYAN), ("(loki)", SOFT)],
    [("tool ", MUTED), ("query_logs", CYAN), ("(30m)", SOFT)],
    [("tool ", MUTED), ("prometheus", CYAN), ("(mem)", SOFT)],
    [("bot  ", MUTED), ("OOM-killed at 02:14.", INK)],
    [("     ", MUTED), ("Fix: raise mem limit ", INK), ("✓", GREEN)],
]


def woff2(weight, text):
    opts = subset.Options()
    opts.flavor, opts.layout_features, opts.hinting, opts.desubroutinize = "woff2", [], False, True
    opts.name_IDs = [0, 13, 14]  # copyright + OFL notice travel with the embedded subset
    font = TTFont(FONT.format(weight))
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


regular_text = ("".join(t for t, _ in PROMPT) + "".join(TAGS) + META + "> _"
                + AGENT_TITLE + "live" + "".join(s for row in AGENT for s, _ in row))
bold = woff2("Bold", NAME)
regular = woff2("Regular", regular_text)

# --- typing timeline: (seconds, line, chars visible), sampled per keystroke ---
TYPE, DELETE, HOLD, GAP = 0.055, 0.025, 2.4, 0.5
events, t = [], 0.0
for i, line in enumerate(TAGS):
    for n in range(len(line) + 1):
        events.append((t, i, n)); t += TYPE
    t += HOLD - TYPE
    for n in range(len(line) - 1, -1, -1):
        t += DELETE; events.append((t, i, n))
    t += GAP
DUR = t
key_times = ";".join(f"{e[0] / DUR:.5f}" for e in events)

TX, TY, TSIZE = 92, 212, 26
CW = ADV * TSIZE


def smil(attr, values):
    return (f'<animate attributeName="{attr}" dur="{DUR:.3f}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{key_times}" values="{";".join(values)}"/>')


clips, lines = [], []
for i, line in enumerate(TAGS):
    widths = [f"{(n * CW if li == i else 0):.2f}" for _, li, n in events]
    first = len(line) * CW if i == 0 else 0
    clips.append(f'<clipPath id="c{i}"><rect class="clip c{i}" x="{TX}" y="{TY - 30}" width="{first:.2f}" height="40">{smil("width", widths)}</rect></clipPath>')
    lines.append(f'<text x="{TX}" y="{TY}" class="r" font-size="{TSIZE}" fill="{SOFT}" clip-path="url(#c{i})">{line}</text>')
cursor_x = [f"{TX + n * CW + 2:.2f}" for _, _, n in events]

# --- agent panel: rows appear one per second, hold, then clear and replay ---
PX, PY, PW, PH = 820, 56, 324, 188
LOOP, ASIZE = 10, 13
rows = []
for i, row in enumerate(AGENT):
    spans = "".join(f'<tspan fill="{c}">{s}</tspan>' for s, c in row)
    rows.append(f'<text x="{PX + 16}" y="{PY + 62 + i * 22}" class="r" font-size="{ASIZE}">{spans}'
                f'<animate attributeName="opacity" dur="{LOOP}s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;{(0.4 + i) / LOOP:.3f};{8.8 / LOOP:.3f}" values="0;1;0"/></text>')

prompt = "".join(f'<tspan fill="{c}">{t}</tspan>' for t, c in PROMPT)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{NAME}</title>
<desc id="d">{" ".join(TAGS)} {META}.</desc>
<defs>
<style>
@font-face{{font-family:FCB;font-weight:700;src:url(data:font/woff2;base64,{bold}) format("woff2")}}
@font-face{{font-family:FCR;src:url(data:font/woff2;base64,{regular}) format("woff2")}}
text{{font-variant-ligatures:none;white-space:pre}}
.b{{font-family:FCB,"Fira Code",ui-monospace,Menlo,Consolas,monospace;font-weight:700}}
.r{{font-family:FCR,"Fira Code",ui-monospace,Menlo,Consolas,monospace}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.blink{{animation:none}}}}
</style>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{LINE}"/></pattern>
<radialGradient id="glow" cx="0.82" cy="0.5" r="0.55"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.16"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
{"".join(clips)}
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="#0A0F1A"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.7"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/>

<circle cx="58" cy="44" r="6" fill="#FF5F57"/><circle cx="80" cy="44" r="6" fill="#FEBC2E"/><circle cx="102" cy="44" r="6" fill="#28C840"/>
<text x="64" y="96" class="r" font-size="18">{prompt}</text>
<text x="62" y="160" class="b" font-size="66" fill="{INK}">{NAME}</text>
<text x="64" y="{TY}" class="r" font-size="{TSIZE}" fill="{CYAN}">&gt;</text>
{"".join(lines)}
<g class="blink"><rect x="{TX + len(TAGS[0]) * CW + 2:.2f}" y="{TY - 22}" width="13" height="27" fill="{CYAN}" opacity="0.85">{smil("x", cursor_x)}</rect></g>
<text x="64" y="262" class="r" font-size="15" fill="{MUTED}">{META}</text>

<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10" fill="#060A12" stroke="{LINE}"/>
<text x="{PX + 16}" y="{PY + 26}" class="r" font-size="12" fill="{MUTED}">{AGENT_TITLE}</text>
<circle cx="{PX + PW - 54}" cy="{PY + 22}" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="{PX + PW - 14}" y="{PY + 26}" class="r" font-size="12" fill="{GREEN}" text-anchor="end">live</text>
<line x1="{PX}" y1="{PY + 38}" x2="{PX + PW}" y2="{PY + 38}" stroke="{LINE}"/>
{"".join(rows)}
</svg>
'''

open(OUT, "w").write(svg)
print(f"{OUT}: {len(svg) / 1024:.1f} KB, loop {DUR:.1f}s")

# self-check: text must stay clear of (and inside) the agent panel
widest = max(len(l) for l in TAGS) * CW + TX + 16
assert widest < PX - 24, f"tagline overlaps agent panel ({widest:.0f} >= {PX - 24})"
assert len(META) * ADV * 15 + 64 < PX - 24, "meta line overlaps agent panel"
assert max(sum(len(s) for s, _ in r) for r in AGENT) * ADV * ASIZE + 32 < PW, "agent log row overflows the panel"
assert PY + 62 + (len(AGENT) - 1) * 22 < PY + PH - 12, "agent log rows overflow the panel"
assert events[0][0] == 0 and all(a[0] < b[0] for a, b in zip(events, events[1:])), "keyTimes not increasing"
