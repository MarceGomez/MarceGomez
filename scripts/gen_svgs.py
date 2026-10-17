"""Genera los SVG animados del perfil (VS Code, pipeline y red neuronal del stack) con la paleta Gruvbox Dark.

Uso: python scripts/gen_svgs.py assets
"""
import base64
import json
import math
import random
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# Paleta Gruvbox Dark — cambia aquí para re-tematizar todo
G = dict(
    bg0h="#1d2021", bg0="#282828", bg0s="#32302f", bg1="#3c3836", bg2="#504945", bg3="#665c54",
    fg="#ebdbb2", fg4="#a89984", gray="#928374",
    red="#fb4934", green="#b8bb26", yellow="#fabd2f", blue="#83a598",
    purple="#d3869b", aqua="#8ec07c", orange="#fe8019",
)

MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, ui-monospace, SFMono-Regular, Menlo, monospace"
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
FS, CW = 13, 7.8  # tamaño de fuente y ancho fijo por carácter (cada carácter se posiciona explícitamente)


def kt(times, total):
    return ";".join(f"{min(t / total, 1):.4f}" for t in times)


def mono(x, y, segs, attrs=""):
    """Texto monoespaciado con cada carácter en una posición fija, sin importar la fuente que tenga el visitante."""
    out, i = [], 0
    for s, c in segs:
        xs = " ".join(f"{x + (i + k) * CW:.1f}" for k in range(len(s)))
        out.append(f'<tspan x="{xs}" fill="{c}">{escape(s)}</tspan>')
        i += len(s)
    return f'<text y="{y}" {attrs} xml:space="preserve">{"".join(out)}</text>'


def keep_spaces(svg):
    """Convierte espacios dobles del texto en NBSP para que los navegadores no los colapsen."""
    return re.sub(r">([^<]*)<", lambda m: ">" + m.group(1).replace("  ", "  ") + "<", svg)


def seglen(segs):
    return sum(len(s) for s, _ in segs)


# --------------------------------------------------------------------------- VS Code
def vscode():
    W, H = 900, 520
    TB, SB = 34, 24            # alto de barra de título y barra de estado
    AB, SW = 48, 190           # ancho de barra de actividad y explorador
    EX = AB + SW               # x donde empieza el editor
    PY = 322                   # y donde empieza el panel de terminal
    p = []

    # ventana
    p.append(f'<rect width="{W}" height="{H}" rx="10" fill="{G["bg0"]}"/>')
    p.append(f'<path d="M0 10a10 10 0 0 1 10-10h{W - 20}a10 10 0 0 1 10 10v{TB - 10}H0z" fill="{G["bg0h"]}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        p.append(f'<circle cx="{20 + i * 20}" cy="17" r="6" fill="{c}"/>')
    p.append(f'<text x="{W / 2}" y="21.5" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{G["fg4"]}">perfil.yml — MarceGomez — Visual Studio Code</text>')

    # barra de actividad
    p.append(f'<rect x="0" y="{TB}" width="{AB}" height="{H - TB - SB}" fill="{G["bg0h"]}"/>')
    p.append(f'<rect x="0" y="{TB + 10}" width="2" height="30" fill="{G["orange"]}"/>')
    ic = G["fg4"]
    p.append(f'<g fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
             # archivos (activo)
             f'<path d="M18 {TB + 18}h8l5 5v13h-13z M26 {TB + 18}v5h5" stroke="{G["fg"]}"/>'
             # buscar
             f'<circle cx="23" cy="{TB + 70}" r="6" stroke="{ic}"/><path d="M27.5 {TB + 74.5}l5 5" stroke="{ic}"/>'
             # git
             f'<circle cx="19" cy="{TB + 108}" r="2.5" stroke="{ic}"/><circle cx="19" cy="{TB + 126}" r="2.5" stroke="{ic}"/>'
             f'<circle cx="30" cy="{TB + 113}" r="2.5" stroke="{ic}"/><path d="M19 {TB + 110.5}v13 M30 {TB + 115.5}c0 5-11 4-11 8" stroke="{ic}"/>'
             # depurar
             f'<path d="M18 {TB + 152}l14 8-14 8z" stroke="{ic}"/>'
             # extensiones
             f'<path d="M17 {TB + 196}h6v6h-6z M25 {TB + 196}h6v6h-6z M17 {TB + 204}h6v6h-6z M27 {TB + 202}l4-4 4 4-4 4z" stroke="{ic}"/>'
             # cuenta y ajustes
             f'<circle cx="24" cy="{H - SB - 60}" r="7" stroke="{ic}"/><circle cx="24" cy="{H - SB - 25}" r="6" stroke="{ic}" stroke-dasharray="3 2"/>'
             f'</g>')
    p.append(f'<circle cx="32" cy="{TB + 107}" r="6" fill="{G["orange"]}"/>'
             f'<text x="32" y="{TB + 110.5}" text-anchor="middle" font-family="{SANS}" font-size="9" font-weight="700" fill="{G["bg0h"]}">7</text>')

    # explorador
    p.append(f'<rect x="{AB}" y="{TB}" width="{SW}" height="{H - TB - SB}" fill="{G["bg0s"]}"/>')
    p.append(f'<g font-family="{SANS}" font-size="12">')
    p.append(f'<text x="{AB + 16}" y="{TB + 24}" font-size="11" letter-spacing="1" fill="{G["fg4"]}">EXPLORADOR</text>')
    p.append(f'<text x="{AB + 8}" y="{TB + 50}" font-size="11" font-weight="700" fill="{G["fg"]}">⌄ MARCEGOMEZ</text>')
    tree = [
        ("›", ".github", None, 0), ("›", "assets", None, 0), ("›", "scripts", None, 0),
        ("", "deploy.sh", G["green"], 1), ("", "perfil.yml", G["purple"], 1), ("", "README.md", G["blue"], 1),
    ]
    for i, (chev, name, col, _) in enumerate(tree):
        y = TB + 74 + i * 22
        if name == "perfil.yml":
            p.append(f'<rect x="{AB}" y="{y - 15}" width="{SW}" height="22" fill="{G["bg1"]}"/>'
                     f'<rect x="{AB}" y="{y - 15}" width="2" height="22" fill="{G["orange"]}"/>')
        if chev:
            p.append(f'<text x="{AB + 18}" y="{y}" fill="{G["fg4"]}">{chev}</text>'
                     f'<path d="M{AB + 30} {y - 9}h5l2 2h7v8h-14z" fill="{G["yellow"]}" opacity=".8"/>'
                     f'<text x="{AB + 50}" y="{y}" fill="{G["fg"]}">{name}</text>')
        else:
            p.append(f'<rect x="{AB + 32}" y="{y - 9}" width="9" height="9" rx="2" fill="{col}"/>'
                     f'<text x="{AB + 50}" y="{y}" fill="{G["fg"] if name == "perfil.yml" else G["fg4"]}">{name}</text>')
    p.append(f'<line x1="{AB}" y1="{H - SB - 56}" x2="{EX}" y2="{H - SB - 56}" stroke="{G["bg1"]}"/>')
    p.append(f'<text x="{AB + 8}" y="{H - SB - 36}" font-size="11" font-weight="700" fill="{G["fg4"]}">› ESQUEMA</text>')
    p.append(f'<text x="{AB + 8}" y="{H - SB - 14}" font-size="11" font-weight="700" fill="{G["fg4"]}">› LÍNEA DE TIEMPO</text>')
    p.append('</g>')

    # pestañas
    p.append(f'<rect x="{EX}" y="{TB}" width="{W - EX}" height="34" fill="{G["bg0h"]}"/>')
    tabs = [("perfil.yml", G["purple"], True), ("deploy.sh", G["green"], False), ("README.md", G["blue"], False)]
    tx = EX
    for name, col, active in tabs:
        w = 124
        if active:
            p.append(f'<rect x="{tx}" y="{TB}" width="{w}" height="34" fill="{G["bg0"]}"/>'
                     f'<rect x="{tx}" y="{TB}" width="{w}" height="2" fill="{G["orange"]}"/>')
        else:
            p.append(f'<line x1="{tx + w}" y1="{TB + 6}" x2="{tx + w}" y2="{TB + 28}" stroke="{G["bg1"]}"/>')
        p.append(f'<rect x="{tx + 14}" y="{TB + 13}" width="9" height="9" rx="2" fill="{col}"/>'
                 f'<text x="{tx + 30}" y="{TB + 22}" font-family="{SANS}" font-size="12" fill="{G["fg"] if active else G["gray"]}" font-style="{"normal" if active else "italic"}">{name}</text>'
                 f'<text x="{tx + w - 18}" y="{TB + 22}" font-family="{SANS}" font-size="12" fill="{G["fg4"] if active else G["bg2"]}">×</text>')
        tx += w
    p.append(f'<text x="{EX + 14}" y="{TB + 52}" font-family="{SANS}" font-size="11.5" fill="{G["gray"]}">MarceGomez  ›  perfil.yml  ›  certificaciones</text>')

    # código
    code = [
        [("# perfil.yml · Marcela Gómez", G["gray"])],
        [("nombre", G["blue"]), (": ", G["fg"]), ('"Marcela Gómez"', G["green"])],
        [("rol", G["blue"]), (": ", G["fg"]), ('"Ingeniera de Software"', G["green"])],
        [("experiencia", G["blue"]), (": ", G["fg"]), ("5+", G["purple"]), (" años", G["fg"])],
        [("foco", G["blue"]), (":", G["fg"])],
        [("  - ", G["orange"]), ("devops", G["fg"])],
        [("  - ", G["orange"]), ("dataops", G["fg"])],
        [("  - ", G["orange"]), ("cloud", G["fg"])],
        [("nubes", G["blue"]), (": ", G["fg"]), ("[", G["orange"]), ("aws", G["fg"]), (", ", G["fg"]), ("azure", G["fg"]), ("]", G["orange"])],
        [("certificaciones", G["blue"]), (": ", G["fg"]), ("[", G["orange"]), ("ibm-scrum-master, scrum-foundation, bi-foundation", G["fg"]), ("]", G["orange"])],
        [("busco", G["blue"]), (": ", G["fg"]), ('"equipos donde la innovación sea el sello"', G["green"])],
    ]
    CY, LH, CX = TB + 78, 19, EX + 52
    cur = len(code) - 1
    p.append(f'<rect x="{EX}" y="{CY + cur * LH - 14}" width="{W - EX - 62}" height="{LH}" fill="{G["bg0s"]}"/>')
    p.append(f'<g font-family="{MONO}" font-size="{FS}">')
    for i, segs in enumerate(code):
        y = CY + i * LH
        p.append(f'<text x="{EX + 36}" y="{y}" text-anchor="end" fill="{G["fg"] if i == cur else G["bg3"]}">{i + 1}</text>')
        p.append(mono(CX, y, segs))
    # guías de indentación
    p.append(f'<line x1="{CX + 1}" y1="{CY + 5 * LH - 13}" x2="{CX + 1}" y2="{CY + 7 * LH + 4}" stroke="{G["bg1"]}"/>')
    ccx = CX + seglen(code[cur]) * CW + 1
    p.append(f'<rect x="{ccx}" y="{CY + cur * LH - 13}" width="2" height="17" fill="{G["fg"]}">'
             f'<animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" calcMode="discrete" values="1;0" keyTimes="0;.5"/></rect>')
    p.append('</g>')

    # minimapa
    MX = W - 56
    p.append(f'<rect x="{MX - 6}" y="{TB + 60}" width="62" height="{PY - TB - 60}" fill="{G["bg0"]}"/>')
    for i, segs in enumerate(code):
        x = MX
        for s, c in segs:
            w = len(s.rstrip()) * 0.75
            if s.strip():
                p.append(f'<rect x="{x + (len(s) - len(s.lstrip())) * 0.75:.1f}" y="{TB + 66 + i * 4}" width="{w:.1f}" height="2" fill="{c}" opacity=".7"/>')
            x += len(s) * 0.75
    p.append(f'<rect x="{MX - 6}" y="{TB + 62}" width="62" height="50" fill="{G["fg"]}" opacity=".06"/>')

    # panel de terminal
    p.append(f'<rect x="{EX}" y="{PY}" width="{W - EX}" height="{H - PY - SB}" fill="{G["bg0h"]}"/>')
    p.append(f'<line x1="{EX}" y1="{PY}" x2="{W}" y2="{PY}" stroke="{G["bg1"]}"/>')
    px = EX + 16
    for name in ["PROBLEMAS", "SALIDA", "CONSOLA DE DEPURACIÓN", "TERMINAL", "PUERTOS"]:
        active = name == "TERMINAL"
        p.append(f'<text x="{px}" y="{PY + 22}" font-family="{SANS}" font-size="11" letter-spacing=".5" fill="{G["fg"] if active else G["gray"]}">{name}</text>')
        w = len(name) * 7.2 + 4
        if active:
            p.append(f'<rect x="{px}" y="{PY + 30}" width="{w - 4}" height="1.5" fill="{G["orange"]}"/>')
        px += w + 18
    p.append(f'<text x="{W - 16}" y="{PY + 22}" text-anchor="end" font-family="{SANS}" font-size="11.5" fill="{G["fg4"]}">bash  +  ⌄  ⋯  ✕</text>')

    p.append(terminal(EX + 16, PY + 58))

    # barra de estado
    p.append(f'<path d="M0 {H - SB}h{W}v{SB - 10}a10 10 0 0 1-10 10H10a10 10 0 0 1-10-10z" fill="{G["bg1"]}"/>')
    p.append(f'<path d="M0 {H - SB}h40v{SB}H10a10 10 0 0 1-10-10z" fill="{G["orange"]}"/>')
    p.append(f'<text x="20" y="{H - 7.5}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{G["bg0h"]}">&gt;&lt;</text>')
    sy = H - 8
    p.append(f'<g font-family="{SANS}" font-size="11.5" fill="{G["fg"]}">'
             f'<circle cx="56" cy="{sy - 7}" r="2" fill="none" stroke="{G["fg"]}" stroke-width="1.3"/>'
             f'<circle cx="56" cy="{sy + 1}" r="2" fill="none" stroke="{G["fg"]}" stroke-width="1.3"/>'
             f'<circle cx="63" cy="{sy - 4}" r="2" fill="none" stroke="{G["fg"]}" stroke-width="1.3"/>'
             f'<text x="70" y="{sy}">main</text>'
             f'<text x="112" y="{sy}">⟳</text>'
             f'<text x="136" y="{sy}">⊗ 0   ⚠ 0</text>'
             f'<text x="{W - 14}" y="{sy}" text-anchor="end">Lín. 11, col. 48    Espacios: 2    UTF-8    YAML    Gruvbox Dark    ✓ Prettier</text>'
             f'</g>')

    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Ventana de VS Code: perfil.yml de Marcela Gómez, Ingeniera de Software — DevOps, DataOps y Cloud">\n'
            + "\n".join(p) + "\n</svg>\n")


def terminal(X0, Y0):
    LH, TOTAL, TYPE = 20, 13.0, 0.06
    prompt = [("marcela@devops", G["green"]), (" ", G["fg"]), ("~/MarceGomez", G["blue"]), (" (main)", G["yellow"]), (" $ ", G["fg4"])]
    P = seglen(prompt)
    lines = [
        ("cmd", prompt + [("whoami", G["fg"])]),
        ("out", [("Marcela Gómez", G["yellow"]), (" · Ingeniera de Software · ", G["fg"]), ("DevOps | DataOps | Cloud", G["aqua"])]),
        ("cmd", prompt + [("./deploy.sh --ideas --env produccion", G["fg"])]),
        ("bar", []),
        ("out", [("✔ ", G["green"]), ("innovación desplegada en producción", G["green"]), ("  (1.2s)", G["gray"])]),
        ("cmd", prompt),
    ]
    parts, clips, cursor = [], [], []
    now, reset = 0.6, TOTAL - 0.3
    for i, (kind, segs) in enumerate(lines):
        y = Y0 + i * LH
        n = seglen(segs)
        if kind == "bar":
            bar_y, bar_s, bar_e = y, now, now + 1.6
            cursor.append((now, -100, y))
            now = bar_e + 0.15
            continue
        if kind == "cmd":
            times, widths = [0, now], [0, P * CW]
            cursor.append((now, X0 + P * CW, y))
            now += 0.45
            for c in range(P + 1, n + 1):
                times.append(now)
                widths.append(c * CW)
                cursor.append((now, X0 + c * CW, y))
                now += TYPE
            now += 0.3
        else:
            times, widths = [0, now], [0, n * CW + 30]
            cursor.append((now, -100, y))
            now += 0.2
        times.append(reset)
        widths.append(0)
        clips.append(f'<clipPath id="t{i}"><rect x="{X0 - 2}" y="{y - 15}" height="{LH}" width="0">'
                     f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
                     f'values="{";".join(f"{w:.1f}" for w in widths)}" keyTimes="{kt(times, TOTAL)}"/></rect></clipPath>')
        parts.append(mono(X0, y, segs, f'clip-path="url(#t{i})"'))

    bw = 260
    bk = kt([0, bar_s, bar_e, reset, TOTAL], TOTAL)
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="0;1;1;0;0" keyTimes="{bk}"/>'
        + mono(X0, bar_y, [("[build]", G["orange"])])
        + f'<rect x="{X0 + 9 * CW}" y="{bar_y - 10}" width="{bw}" height="10" rx="2" fill="{G["bg1"]}"/>'
        f'<rect x="{X0 + 9 * CW}" y="{bar_y - 10}" width="0" height="10" rx="2" fill="url(#gb)">'
        f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" values="0;0;{bw};{bw};0" keyTimes="{bk}"/></rect>'
        + mono(X0 + 9 * CW + bw + 12, bar_y, [("100%", G["fg"]), ("  0 errores", G["gray"])])
        + '</g>')

    cursor.insert(0, (0, X0 + P * CW, Y0))
    cursor.append((reset, X0 + P * CW, Y0))
    ct = kt([c[0] for c in cursor], TOTAL)
    parts.append(
        f'<rect width="{CW:.1f}" height="16" fill="{G["fg"]}" opacity=".85" y="{Y0 - 13}">'
        f'<animate attributeName="x" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="{";".join(f"{c[1]:.1f}" for c in cursor)}" keyTimes="{ct}"/>'
        f'<animate attributeName="y" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="{";".join(str(c[2] - 13) for c in cursor)}" keyTimes="{ct}"/>'
        f'<animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="discrete" values=".85;0" keyTimes="0;.5"/></rect>')

    return (f'<defs><linearGradient id="gb" x1="0" x2="1"><stop offset="0" stop-color="{G["orange"]}"/>'
            f'<stop offset=".5" stop-color="{G["yellow"]}"/><stop offset="1" stop-color="{G["green"]}"/></linearGradient>'
            + "".join(clips) + f'</defs><g font-family="{MONO}" font-size="{FS}">' + "".join(parts) + '</g>')


# --------------------------------------------------------------------------- pipeline
def pipeline():
    W, H = 900, 236
    stages = [
        ("#", "Plan", "Scrum · Jira", G["red"]),
        ("</>", "Code", "Python · TS · JS", G["orange"]),
        ("{ }", "Build", "Django · NestJS", G["yellow"]),
        ("✓", "Test", "Postman · Swagger", G["green"]),
        ("↑", "Deploy", "AWS · Azure · Nginx", G["aqua"]),
        ("~", "Monitor", "BI · Postgres", G["blue"]),
    ]
    TOTAL, RUN = 8.0, 5.0
    x0, gap, cy = 95, 142, 124
    xs = [x0 + i * gap for i in range(len(stages))]
    xe = xs[-1]
    nodes = []
    for i, (icon, name, sub, col) in enumerate(stages):
        x = xs[i]
        k = kt([0, RUN * i / (len(stages) - 1), TOTAL - 0.5, TOTAL], TOTAL)
        anim = f'dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}"'
        nodes.append(
            f'<circle cx="{x}" cy="{cy}" r="30" fill="{col}" opacity="0" filter="url(#soft)"><animate attributeName="opacity" {anim} values="0;.45;0;0"/></circle>'
            f'<circle cx="{x}" cy="{cy}" r="26" fill="{G["bg0h"]}" stroke="{G["bg2"]}" stroke-width="2.5"><animate attributeName="stroke" {anim} values="{G["bg2"]};{col};{G["bg2"]};{G["bg2"]}"/></circle>'
            f'<text x="{x}" y="{cy + 6}" text-anchor="middle" font-size="17" font-weight="700" fill="{G["bg3"]}">{escape(icon)}<animate attributeName="fill" {anim} values="{G["bg3"]};{col};{G["bg3"]};{G["bg3"]}"/></text>'
            f'<text x="{x}" y="{cy + 56}" text-anchor="middle" font-size="14" font-weight="700" fill="{G["fg"]}">{name}</text>'
            f'<text x="{x}" y="{cy + 76}" text-anchor="middle" font-size="11.5" fill="{G["gray"]}">{escape(sub)}</text>')
    kr = kt([0, RUN, TOTAL - 0.5, TOTAL], TOTAL)
    kp = kt([0, RUN, RUN + 0.01, TOTAL - 0.5, TOTAL], TOTAL)
    ks = kt([0, RUN, TOTAL - 0.5], TOTAL)
    stops = "".join(f'<stop offset="{i / 5:.2f}" stop-color="{s[3]}"/>' for i, s in enumerate(stages))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Pipeline animado: Plan, Code, Build, Test, Deploy, Monitor">
<defs>
<linearGradient id="prog" gradientUnits="userSpaceOnUse" x1="{x0}" x2="{xe}">{stops}</linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="{W}" height="{H}" rx="10" fill="{G["bg0"]}"/>
<path d="M0 10a10 10 0 0 1 10-10h{W - 20}a10 10 0 0 1 10 10v34H0z" fill="{G["bg0h"]}"/>
<g font-family="{MONO}">
<text x="22" y="28" font-size="12.5" fill="{G["gray"]}"><tspan fill="{G["orange"]}">▶</tspan>  carrera.yml  <tspan fill="{G["bg3"]}">│</tspan>  <tspan fill="{G["fg"]}" font-weight="700">marcela/carrera</tspan>  <tspan fill="{G["bg3"]}">│</tspan>  <tspan fill="{G["yellow"]}">main</tspan>  <tspan fill="{G["bg3"]}">│</tspan>  5+ años en producción</text>
<g font-size="12.5" font-weight="700">
<text x="{W - 22}" y="28" text-anchor="end" fill="{G["yellow"]}">● en ejecución<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="1;0;1" keyTimes="{ks}"/></text>
<text x="{W - 22}" y="28" text-anchor="end" fill="{G["green"]}" opacity="0">✔ exitoso<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="0;1;0" keyTimes="{ks}"/></text>
</g>
<line x1="{x0}" y1="{cy}" x2="{xe}" y2="{cy}" stroke="{G["bg2"]}" stroke-width="2" stroke-dasharray="5 6"/>
<rect x="{x0}" y="{cy - 2}" height="4" width="0" rx="2" fill="url(#prog)"><animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" values="0;{xe - x0};{xe - x0};0" keyTimes="{kr}"/></rect>
{chr(10).join(nodes)}
<g>
<circle r="11" fill="{G["fg"]}" opacity=".5" filter="url(#soft)"/><circle r="5" fill="{G["fg"]}"/>
<animateTransform attributeName="transform" type="translate" dur="{TOTAL}s" repeatCount="indefinite" values="{x0} {cy};{xe} {cy};{xe} {cy};{xe} {cy};{x0} {cy}" keyTimes="{kp}"/>
<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" values="1;1;0;0;0" keyTimes="{kp}"/>
</g>
</g>
</svg>
'''


# --------------------------------------------------------------------------- red neuronal (stack + certificaciones)
HERE = Path(__file__).parent
ICONS = json.loads((HERE / "icons.json").read_text(encoding="utf-8"))

# (dominio, color, [(etiqueta, slug de Simple Icons | texto | badge:archivo)])
NETWORK = [
    ("IA", G["purple"], [
        ("Claude", "claude"), ("Claude Code", ">_"), ("ChatGPT", "openai"),
        ("Gemini", "googlegemini"), ("ElevenLabs", "elevenlabs"), ("MCP", "modelcontextprotocol"),
    ]),
    ("Cloud", G["aqua"], [
        ("AWS", "amazonaws"), ("Azure", "microsoftazure"), ("Cloudflare", "cloudflare"),
    ]),
    ("DevOps", G["blue"], [
        ("Azure DevOps", "azuredevops"), ("GitHub Actions", "githubactions"), ("Git", "git"),
        ("GitHub", "github"), ("Nginx", "nginx"), ("VS Code", "visualstudiocode"),
    ]),
    ("Datos", "#689d6a", [
        ("PostgreSQL", "postgresql"), ("MySQL", "mysql"),
    ]),
    ("Certificaciones", G["yellow"], [
        ("IBM Scrum Master", "badge:ibm-scrum-master"), ("Scrum Foundation", "badge:scrum-foundation"),
        ("BI Foundation", "badge:bi-foundation"),
    ]),
    ("Agile & APIs", G["orange"], [
        ("Postman", "postman"), ("Swagger", "swagger"), ("Jira", "jira"),
        ("Confluence", "confluence"), ("Trello", "trello"),
    ]),
    ("Diseño", G["red"], [
        ("Figma", "figma"), ("Illustrator", "adobeillustrator"), ("Sketch", "sketch"),
    ]),
    ("Lenguajes", "#d79921", [
        ("Python", "python"), ("TypeScript", "typescript"), ("JavaScript", "javascript"),
        ("HTML5", "html5"), ("Sass", "sass"),
    ]),
    ("Frameworks", G["green"], [
        ("Django", "django"), ("NestJS", "nestjs"), ("Node.js", "nodedotjs"),
        ("Vue.js", "vuedotjs"), ("Symfony", "symfony"), ("Bootstrap", "bootstrap"),
    ]),
]


def network():
    W, H = 900, 910
    cx, cy = 450, 462
    R_CORE, R_HUB, R_IN, R_OUT, SX = 64, 180, 290, 366, 1.02
    rnd = random.Random(7)  # determinista: el SVG no cambia entre ejecuciones

    def weight(leaf):
        return 2.5 if leaf[1].startswith("badge:") else 1.0

    GAP = 1.2
    total = sum(sum(weight(l) for l in leaves) + GAP for _, _, leaves in NETWORK)
    unit = 2 * math.pi / total
    first = NETWORK[0]
    a = -math.pi / 2 - (sum(weight(l) for l in first[2]) + GAP) * unit / 2

    def pt(ang, r):
        return cx + math.cos(ang) * r * SX, cy + math.sin(ang) * r

    defs, syn, pulses, nodes, labels = [], [], [], [], []
    n_syn = 0
    for name, col, leaves in NETWORK:
        span = (sum(weight(l) for l in leaves) + GAP) * unit
        mid = a + span / 2
        hx, hy = pt(mid, R_HUB)

        # sinapsis núcleo → dominio
        sx, sy = pt(mid, R_CORE)
        ox, oy = -math.sin(mid) * 28, math.cos(mid) * 28
        d = f"M{sx:.1f} {sy:.1f}Q{(sx + hx) / 2 + ox:.1f} {(sy + hy) / 2 + oy:.1f} {hx:.1f} {hy:.1f}"
        syn.append(f'<path d="{d}" stroke="{col}" stroke-opacity=".55" stroke-width="2"/>')
        dur, beg = rnd.uniform(1.8, 2.8), rnd.uniform(0, 3)
        pulses.append(f'<circle r="3.2" fill="{col}" filter="url(#glow)"><animateMotion dur="{dur:.2f}s" begin="-{beg:.2f}s" repeatCount="indefinite" path="{d}"/></circle>')
        n_syn += 1

        # neuronas del dominio
        pos = a + GAP * unit / 2
        for i, leaf in enumerate(leaves):
            label, icon = leaf
            w = weight(leaf)
            ang = pos + w * unit / 2
            pos += w * unit
            is_badge = icon.startswith("badge:")
            r_leaf = 31 if is_badge else 21
            rad = (R_OUT - 14 if i % 2 else R_IN + 20) if is_badge else (R_OUT if i % 2 else R_IN)
            lx, ly = pt(ang, rad)
            mx, my = pt(mid + (ang - mid) * 0.35, (R_HUB + rad) / 2)
            d = f"M{hx:.1f} {hy:.1f}Q{mx:.1f} {my:.1f} {lx:.1f} {ly:.1f}"
            syn.append(f'<path d="{d}" stroke="{col}" stroke-opacity=".28" stroke-width="1.2"/>')
            dur, beg = rnd.uniform(2.4, 4.2), rnd.uniform(0, 4)
            timing = f'dur="{dur:.2f}s" begin="-{beg:.2f}s" repeatCount="indefinite"'
            pulses.append(f'<circle r="2.4" fill="{col}" filter="url(#glow)"><animateMotion {timing} path="{d}"/></circle>')
            n_syn += 1

            # destello sincronizado con la llegada del pulso
            nodes.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{r_leaf + 7}" fill="{col}" opacity="0" filter="url(#soft)">'
                         f'<animate attributeName="opacity" {timing} values="0;0;.6;0" keyTimes="0;.86;.93;1"/></circle>')
            nodes.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{r_leaf}" fill="url(#cell)" stroke="{col}" stroke-width="1.6"/>'
                         f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{r_leaf + 4}" fill="none" stroke="{col}" stroke-opacity=".25" stroke-dasharray="2 4"/>')
            if is_badge:
                b64 = base64.b64encode((HERE / "badges" / f"{icon[6:]}.png").read_bytes()).decode()
                s = 46
                nodes.append(f'<image x="{lx - s / 2:.1f}" y="{ly - s / 2:.1f}" width="{s}" height="{s}" href="data:image/png;base64,{b64}"/>')
            elif icon in ICONS:
                s = 20
                nodes.append(f'<path transform="translate({lx - s / 2:.1f} {ly - s / 2:.1f}) scale({s / 24:.4f})" fill="{G["fg"]}" d="{ICONS[icon]}"/>')
            else:
                nodes.append(f'<text x="{lx:.1f}" y="{ly + 4.5:.1f}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{G["fg"]}">{escape(icon)}</text>')

            # etiqueta: hacia afuera en el anillo externo, hacia adentro en el interno
            out = rad >= R_OUT - 20 or is_badge
            ux, uy = math.cos(ang) * (1 if out else -1), math.sin(ang) * (1 if out else -1)
            if abs(math.cos(ang)) > 0.55:  # nodos laterales: etiqueta debajo para no salirse del lienzo
                tx, ty, anchor = lx, ly + r_leaf + 15, "middle"
            else:
                tx, ty = lx + ux * (r_leaf + 9), ly + uy * (r_leaf + 9) + 3.5
                if uy > 0.5:
                    ty += 6
                anchor = "middle" if abs(ux) < 0.45 else ("start" if ux > 0 else "end")
            labels.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" fill="{G["fg4"]}">{escape(label)}</text>')

        # dominio (píldora)
        pw = len(name) * 7.4 + 26
        nodes.append(f'<rect x="{hx - pw / 2:.1f}" y="{hy - 13:.1f}" width="{pw:.1f}" height="26" rx="13" fill="{G["bg0h"]}" stroke="{col}" stroke-width="1.6"/>'
                     f'<text x="{hx:.1f}" y="{hy + 4:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing=".5" fill="{col}">{escape(name.upper())}</text>')
        a += span

    n_nodes = sum(len(l) for _, _, l in NETWORK)
    core = (
        f'<circle cx="{cx}" cy="{cy}" r="{R_CORE}" fill="none" stroke="{G["orange"]}" stroke-width="2" opacity="0">'
        f'<animate attributeName="r" values="{R_CORE};{R_CORE + 46}" dur="3s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".6;0" dur="3s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="{R_CORE + 14}" fill="url(#aura)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{R_CORE}" fill="url(#core)" stroke="{G["orange"]}" stroke-width="2"/>'
        f'<g><circle cx="{cx}" cy="{cy}" r="{R_CORE - 8}" fill="none" stroke="{G["yellow"]}" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="14 8 3 8"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></g>'
        f'<g><circle cx="{cx}" cy="{cy}" r="{R_CORE + 6}" fill="none" stroke="{G["orange"]}" stroke-opacity=".4" stroke-dasharray="1 6"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="30s" repeatCount="indefinite"/></g>'
        f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="800" letter-spacing="1.5" fill="{G["fg"]}">MARCELA</text>'
        f'<text x="{cx}" y="{cy + 15}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{G["orange"]}">GÓMEZ</text>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Red neuronal del stack y certificaciones de Marcela Gómez">
<defs>
<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{G["bg1"]}"/></pattern>
<radialGradient id="cell"><stop offset="0" stop-color="{G["bg0s"]}"/><stop offset="1" stop-color="{G["bg0h"]}"/></radialGradient>
<radialGradient id="core"><stop offset="0" stop-color="#3a2a1c"/><stop offset="1" stop-color="{G["bg0h"]}"/></radialGradient>
<radialGradient id="aura"><stop offset=".6" stop-color="{G["orange"]}" stop-opacity=".25"/><stop offset="1" stop-color="{G["orange"]}" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".7"><stop offset=".55" stop-color="{G["bg0"]}" stop-opacity="0"/><stop offset="1" stop-color="{G["bg0h"]}" stop-opacity=".9"/></radialGradient>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<rect width="{W}" height="{H}" rx="12" fill="{G["bg0"]}"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#grid)"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#vig)"/>
<g font-family="{MONO}" font-size="11.5">
<text x="22" y="30" fill="{G["gray"]}"><tspan fill="{G["orange"]}">◉</tspan> red_neuronal<tspan fill="{G["fg4"]}">.stack()</tspan></text>
<text x="{W - 22}" y="30" text-anchor="end" fill="{G["gray"]}">{n_nodes} neuronas · {n_syn} sinapsis · <tspan fill="{G["green"]}">activa</tspan></text>
</g>
<g fill="none">{"".join(syn)}</g>
{"".join(pulses)}
{"".join(nodes)}
{core}
<g font-family="{SANS}" font-size="11">{"".join(labels)}</g>
</svg>
'''


(OUT / "vscode.svg").write_text(keep_spaces(vscode()), encoding="utf-8")
(OUT / "network.svg").write_text(network(), encoding="utf-8")
(OUT / "pipeline.svg").write_text(keep_spaces(pipeline()), encoding="utf-8")
print("ok", sorted(p.name for p in OUT.iterdir()))
