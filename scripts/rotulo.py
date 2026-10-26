#!/usr/bin/env python3
"""Rótulo LED de autobús animado para el README de GitHub de nfurniel.

Cada LED es un círculo, sin fuentes externas: GitHub muestra el SVG dentro
de <img>, donde no se puede cargar nada de fuera, pero el CSS sí se anima.
"""
from pathlib import Path
import sys

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/rotulo-bus.svg")

# --- Contenido -------------------------------------------------------------
LINE = "NF"
SCREENS = [
    "NICOLÁS FURNIELES",
    "DESARROLLADOR WEB",
    "REACT + NEXT.JS",
    "AGENTES, RAG Y MCP",
    "PRÓXIMA PARADA:",
    "TU EQUIPO",
]
DWELL, SCROLL = 3.2, 0.6  # segundos por pantalla / duración del scroll

# --- Aspecto ---------------------------------------------------------------
P = 10  # paso entre LEDs, en unidades SVG
R_ON, R_OFF = 3.9, 3.1
LED_ON, LED_OFF = "#FFB31A", "#2B1F09"
SCREEN_BG = "#070503"
BEZEL_TOP, BEZEL_BOTTOM, BEZEL_EDGE = "#2A64BC", "#163E80", "#0E2C5E"
BEZEL, PAD = 20, 12  # grosor del marco / margen negro alrededor de los LEDs

# --- Fuente de matriz de puntos 5x7, ancho variable ------------------------
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    ".": ["..", "..", "..", "..", "..", "##", "##"],
    ":": ["..", "##", "##", "..", "##", "##", ".."],
    ",": ["..", "..", "..", "..", "##", ".#", "#."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
}
ACCENTS = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"}

ROWS = 13  # filas 0-1 tilde, 2 hueco, 3-9 mayúsculas, 10-12 margen
CAP0 = 3
BOX_ROWS = range(1, 12)
BOX_PAD = 2
MARGIN, GAP, TEXT_PAD = 2, 4, 3


def glyph(ch):
    base = ACCENTS.get(ch, ch)
    if base not in FONT:
        raise SystemExit(f"Falta el carácter {ch!r} en la fuente")
    rows = FONT[base]
    w = len(rows[0])
    dots = []
    for r, line in enumerate(rows):
        assert len(line) == w, f"ancho incoherente en {ch!r}"
        dots += [(c, CAP0 + r) for c, v in enumerate(line) if v == "#"]
    if ch in ACCENTS:  # tilde aguda: dos LEDs en diagonal
        dots += [(w // 2 + 1, 0), (w // 2, 1)]
    return w, dots


def layout(text):
    x, items = 0, []
    for ch in text:
        w, _ = glyph(ch)
        items.append((x, ch))
        x += w + 1
    return x - 1, items


def dot(c, r):
    return f'<circle cx="{c * P + P // 2}" cy="{r * P + P // 2}" r="{R_ON}"/>'


line_w, line_items = layout(LINE)
box_w = line_w + 2 * BOX_PAD
text_w = max(layout(s)[0] for s in SCREENS) + 2 * TEXT_PAD
box_x0 = MARGIN
text_x0 = box_x0 + box_w + GAP
COLS = text_x0 + text_w + MARGIN

DW, DH = COLS * P, ROWS * P
O = BEZEL + PAD
W, H = DW + 2 * O, DH + 2 * O

# Glifos reutilizables (uno por carácter) ---------------------------------
chars = sorted({ch for s in SCREENS for ch in s if ch != " "})
defs = "".join(
    f'<g id="g{ord(ch)}">' + "".join(dot(c, r) for c, r in glyph(ch)[1]) + "</g>"
    for ch in chars
)

# Caja de la línea, en negativo (fondo encendido, letras apagadas) -----------
letters = set()
for x, ch in line_items:
    letters |= {(box_x0 + BOX_PAD + x + c, r) for c, r in glyph(ch)[1]}
box = "".join(
    dot(c, r)
    for c in range(box_x0, box_x0 + box_w)
    for r in BOX_ROWS
    if (c, r) not in letters
)

# Pantallas -------------------------------------------------------------------
screens = []
for i, s in enumerate(SCREENS):
    w, items = layout(s)
    x0 = text_x0 + (text_w - w) // 2
    uses = "".join(
        f'<use href="#g{ord(ch)}" xlink:href="#g{ord(ch)}" x="{(x0 + x) * P}"/>'
        for x, ch in items
        if ch != " "
    )
    screens.append(f'<g class="s s{i}">{uses}</g>')

# Animación: cada pantalla entra desde abajo y sale por arriba, fila a fila --
N = len(SCREENS)
T = N * DWELL
a, b, c = SCROLL / T * 100, DWELL / T * 100, (DWELL + SCROLL) / T * 100
delays = "".join(f".s{i}{{animation-delay:{round(i * DWELL, 3):g}s}}" for i in range(1, N))
css = (
    f".s{{animation:roll {T:g}s infinite both}}{delays}"
    "@keyframes roll{"
    f"0%{{transform:translateY({DH}px);animation-timing-function:steps({ROWS},end)}}"
    f"{a:.3f}%{{transform:translateY(0)}}"
    f"{b:.3f}%{{transform:translateY(0);animation-timing-function:steps({ROWS},end)}}"
    f"{c:.3f}%,100%{{transform:translateY(-{DH}px)}}"
    "}"
    "@media (prefers-reduced-motion:reduce){.s{animation:none;visibility:hidden}.s0{visibility:visible}}"
)

title = "Rótulo LED de autobús: " + ", ".join(s.rstrip(":").capitalize() for s in SCREENS)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{title}</title>
<style>{css}</style>
<defs>
<linearGradient id="bz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BEZEL_TOP}"/><stop offset="1" stop-color="{BEZEL_BOTTOM}"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<pattern id="off" width="{P}" height="{P}" patternUnits="userSpaceOnUse"><circle cx="{P / 2:g}" cy="{P / 2:g}" r="{R_OFF}" fill="{LED_OFF}"/></pattern>
<filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="txt"><rect x="{text_x0 * P}" y="0" width="{text_w * P}" height="{DH}"/></clipPath>
{defs}
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="url(#bz)" stroke="{BEZEL_EDGE}" stroke-width="2"/>
<rect x="{BEZEL}" y="{BEZEL}" width="{W - 2 * BEZEL}" height="{H - 2 * BEZEL}" rx="8" fill="{SCREEN_BG}"/>
<g transform="translate({O} {O})">
<rect width="{DW}" height="{DH}" fill="url(#off)"/>
<g fill="{LED_ON}" filter="url(#glow)">
{box}
<g clip-path="url(#txt)">
{chr(10).join(screens)}
</g>
</g>
</g>
<rect x="{BEZEL}" y="{BEZEL}" width="{W - 2 * BEZEL}" height="{H - 2 * BEZEL}" rx="8" fill="url(#glass)"/>
</svg>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"{OUT}  {W}x{H}  matriz {COLS}x{ROWS}  {len(svg.encode()) / 1024:.1f} KB")
