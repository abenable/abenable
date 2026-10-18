"""Generate assets/header.svg for the GitHub profile: terminal card + typed taglines + scope trace.

Edit NAME / TAGS / META below, then from the repo root:
    uv run --with fonttools --with brotli assets/make_header.py assets/header.svg
Needs Fira Code installed (apt install fonts-firacode).
"""
import base64, io, math, sys
from fontTools import subset
from fontTools.ttLib import TTFont

OUT = sys.argv[1]
FONT = "/usr/share/fonts/truetype/firacode/FiraCode-{}.ttf"
ADV = 1200 / 1950  # Fira Code advance width in em, every glyph

W, H = 1200, 300
CYAN, INK, SOFT, MUTED, LINE = "#22D3EE", "#F1F5F9", "#CBD5E1", "#64748B", "#1E293B"

NAME = "Able Abenaitwe"
PROMPT = [("able@makerere", CYAN), (":~$ ", MUTED), ("whoami", SOFT)]
TAGS = [
    "I build AI agents that do real work.",
    "I ship full-stack apps, front to back.",
    "I keep the servers up. Mostly.",
    "I study EE at Makerere University.",
]
META = "Software Engineer @ Feyti Medical Group · Infra Intern @ Marconi · Freelance"
SCOPE = ["CH1  2V/div", "50 Hz", "signal: clean"]


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


regular_text = "".join(t for t, _ in PROMPT) + "".join(TAGS) + META + "".join(SCOPE) + "> _"
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

# --- scope panel: periodic trace scrolled by exactly one period so the loop is seamless ---
PX, PY, PW, PH = 820, 56, 324, 188
mid, period, amp = PY + PH / 2 + 8, 108, 44
pts = []
for k in range(0, int(PW + 2 * period) + 1, 3):
    a = 2 * math.pi * k / period
    y = mid - amp * (math.sin(a) + 0.18 * math.sin(3 * a))
    pts.append(f"{PX + k:.1f},{y:.1f}")
trace = "M" + " L".join(pts)
grid = "".join(f'<line x1="{PX + x}" y1="{PY}" x2="{PX + x}" y2="{PY + PH}"/>' for x in range(36, PW, 36))
grid += "".join(f'<line x1="{PX}" y1="{PY + y}" x2="{PX + PW}" y2="{PY + y}"/>' for y in range(36, PH, 36))

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
<clipPath id="panel"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="10"/></clipPath>
<filter id="phosphor" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
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
<g clip-path="url(#panel)">
<g stroke="{LINE}" stroke-width="1" opacity="0.8">{grid}</g>
<line x1="{PX}" y1="{mid}" x2="{PX + PW}" y2="{mid}" stroke="#334155" stroke-dasharray="2 4"/>
<g>
<animateTransform attributeName="transform" type="translate" from="0 0" to="{-period} 0" dur="2.2s" repeatCount="indefinite"/>
<path d="{trace}" fill="none" stroke="{CYAN}" stroke-width="5" opacity="0.45" filter="url(#phosphor)"/>
<path d="{trace}" fill="none" stroke="{CYAN}" stroke-width="2.2" stroke-linejoin="round"/>
</g>
</g>
<text x="{PX + 14}" y="{PY + 24}" class="r" font-size="12" fill="{MUTED}">{SCOPE[0]}</text>
<text x="{PX + PW - 14}" y="{PY + 24}" class="r" font-size="12" fill="{MUTED}" text-anchor="end">{SCOPE[1]}</text>
<text x="{PX + 14}" y="{PY + PH - 12}" class="r" font-size="12" fill="{CYAN}" opacity="0.8">{SCOPE[2]}</text>
</svg>
'''

open(OUT, "w").write(svg)
print(f"{OUT}: {len(svg) / 1024:.1f} KB, loop {DUR:.1f}s")

# self-check: widest tagline must stay clear of the scope panel
widest = max(len(l) for l in TAGS) * CW + TX + 16
assert widest < PX - 24, f"tagline overlaps scope panel ({widest:.0f} >= {PX - 24})"
assert len(META) * ADV * 15 + 64 < PX - 24, "meta line overlaps scope panel"
assert events[0][0] == 0 and all(a[0] < b[0] for a, b in zip(events, events[1:])), "keyTimes not increasing"
