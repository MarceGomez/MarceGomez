"""Genera los SVG animados del perfil (terminal + pipeline) en modo claro y oscuro.

Uso: python scripts/gen_svgs.py assets
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    "dark": dict(
        bg1="#0d1117", bg2="#161b22", win="#0d1117", bar="#161b22", border="#30363d",
        text="#e6edf3", dim="#8b949e", prompt="#ff79c6", key="#79c0ff", str="#a5d6ff",
        ok="#7ee787", acc1="#ff79c6", acc2="#bd93f9", acc3="#79c0ff", node="#161b22",
        track="#30363d",
    ),
    "light": dict(
        bg1="#ffffff", bg2="#f6f8fa", win="#ffffff", bar="#f6f8fa", border="#d0d7de",
        text="#1f2328", dim="#656d76", prompt="#bf3989", key="#0550ae", str="#0a3069",
        ok="#1a7f37", acc1="#bf3989", acc2="#8250df", acc3="#0969da", node="#f6f8fa",
        track="#d0d7de",
    ),
}

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
FS = 15
CW = FS * 0.6  # ancho aproximado de un carácter monoespaciado


def kt(times, total):
    return ";".join(f"{min(t / total, 1):.4f}" for t in times)


# --------------------------------------------------------------------------- terminal
def terminal(t):
    W, H = 860, 360
    X0, Y0, LH = 36, 92, 25
    TOTAL = 18.0
    TYPE = 0.065  # segundos por carácter

    # cada línea: (tipo, [(texto, color)])  tipo: "cmd" se teclea, "out" aparece de golpe
    lines = [
        ("cmd", [("$ ", t["prompt"]), ("whoami", t["text"])]),
        ("out", [("Marcela Gómez", t["ok"]), (" — Ingeniera de Software", t["text"])]),
        ("cmd", [("$ ", t["prompt"]), ("cat perfil.yml", t["text"])]),
        ("out", [("experiencia", t["key"]), (": ", t["dim"]), ('"5+ años"', t["str"])]),
        ("out", [("foco", t["key"]), (": ", t["dim"]), ("[devops, dataops, cloud]", t["str"])]),
        ("out", [("nubes", t["key"]), (": ", t["dim"]), ("[aws, azure]", t["str"])]),
        ("out", [("busco", t["key"]), (": ", t["dim"]), ('"equipos donde la innovación sea el sello"', t["str"])]),
        ("cmd", [("$ ", t["prompt"]), ("./deploy.sh --ideas --env produccion", t["text"])]),
        ("bar", []),
        ("out", [("✔ ", t["ok"]), ("innovación desplegada con éxito", t["ok"])]),
        ("cmd", [("$ ", t["prompt"])]),
    ]

    parts, clips = [], []
    cursor = []  # (tiempo, x, y)
    now = 0.8
    bar_start = bar_end = 0
    for i, (kind, segs) in enumerate(lines):
        y = Y0 + i * LH
        text = "".join(s for s, _ in segs)
        n = len(text)
        if kind == "bar":
            bar_start, bar_end = now, now + 1.8
            bar_y = y
            cursor.append((now, -100, y))
            now = bar_end + 0.2
            continue
        if kind == "cmd":
            # el prompt aparece de golpe, el comando se teclea
            times, widths = [0, now], [0, 2 * CW]
            cursor.append((now, X0 + 2 * CW, y))
            now += 0.5
            for c in range(3, n + 1):
                times.append(now)
                widths.append(c * CW)
                cursor.append((now, X0 + c * CW, y))
                now += TYPE
            now += 0.35
        else:
            times, widths = [0, now], [0, n * CW + 40]
            cursor.append((now, -100, y))
            now += 0.25
        times.append(TOTAL - 0.4)
        widths.append(0)
        clips.append(
            f'<clipPath id="c{i}"><rect x="{X0 - 4}" y="{y - FS - 2}" height="{LH}" width="0">'
            f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{";".join(f"{w:.1f}" for w in widths)}" keyTimes="{kt(times, TOTAL)}"/></rect></clipPath>'
        )
        tsp = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in segs)
        parts.append(f'<text x="{X0}" y="{y}" clip-path="url(#c{i})" xml:space="preserve">{tsp}</text>')

    # barra de progreso
    bx, bw = X0, 420
    bk = kt([0, bar_start, bar_end, TOTAL - 0.4, TOTAL], TOTAL)
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
        f'values="0;1;1;0;0" keyTimes="{bk}"/>'
        f'<rect x="{bx}" y="{bar_y - 12}" width="{bw}" height="12" rx="6" fill="{t["track"]}"/>'
        f'<rect x="{bx}" y="{bar_y - 12}" width="0" height="12" rx="6" fill="url(#acc)">'
        f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" '
        f'values="0;0;{bw};{bw};0" keyTimes="{bk}"/></rect>'
        f'<text x="{bx + bw + 14}" y="{bar_y}" fill="{t["dim"]}">100%  build #2026 · 0 errores</text></g>'
    )

    # cursor parpadeante
    cursor.insert(0, (0, X0, Y0))
    cursor.append((TOTAL - 0.4, X0, Y0))
    ct = [c[0] for c in cursor]
    parts.append(
        f'<rect width="{CW:.1f}" height="{FS + 2}" fill="{t["prompt"]}" x="{X0}" y="{Y0 - FS + 1}">'
        f'<animate attributeName="x" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
        f'values="{";".join(f"{c[1]:.1f}" for c in cursor)}" keyTimes="{kt(ct, TOTAL)}"/>'
        f'<animate attributeName="y" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
        f'values="{";".join(f"{c[2] - FS + 1}" for c in cursor)}" keyTimes="{kt(ct, TOTAL)}"/>'
        f'<animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="discrete" values="1;0" keyTimes="0;0.5"/>'
        f'</rect>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal animada: Marcela Gómez, Ingeniera de Software — DevOps, DataOps y Cloud">
<defs>
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{t["acc1"]}"/><stop offset=".5" stop-color="{t["acc2"]}"/><stop offset="1" stop-color="{t["acc3"]}"/></linearGradient>
<linearGradient id="glow" x1="0" x2="1"><stop offset="0" stop-color="{t["acc1"]}" stop-opacity=".55"/><stop offset=".5" stop-color="{t["acc2"]}" stop-opacity=".55"/><stop offset="1" stop-color="{t["acc3"]}" stop-opacity=".55"/></linearGradient>
<filter id="blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="10"/></filter>
{"".join(clips)}
</defs>
<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="14" fill="url(#glow)" filter="url(#blur)">
<animate attributeName="opacity" values=".5;1;.5" dur="5s" repeatCount="indefinite"/></rect>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="12" fill="{t["win"]}" stroke="{t["border"]}"/>
<path d="M8 20a12 12 0 0 1 12-12h{W - 40}a12 12 0 0 1 12 12v22H8z" fill="{t["bar"]}"/>
<line x1="8" y1="42" x2="{W - 8}" y2="42" stroke="{t["border"]}"/>
<circle cx="32" cy="25" r="6" fill="#ff5f57"/><circle cx="52" cy="25" r="6" fill="#febc2e"/><circle cx="72" cy="25" r="6" fill="#28c840"/>
<text x="{W / 2}" y="30" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{t["dim"]}">marcela@devops: ~</text>
<rect x="8" y="{H - 11}" width="{W - 16}" height="3" fill="url(#acc)" opacity=".9"/>
<g font-family="{FONT}" font-size="{FS}">
{chr(10).join(parts)}
</g>
</svg>
'''


# --------------------------------------------------------------------------- pipeline
def pipeline(t):
    W, H = 860, 230
    stages = [
        ("#", "Plan", "Scrum · Jira"),
        ("</>", "Code", "Python · TS · JS"),
        ("{ }", "Build", "Django · NestJS"),
        ("✓", "Test", "Postman · Swagger"),
        ("↑", "Deploy", "AWS · Azure · Nginx"),
        ("~", "Monitor", "BI · Postgres"),
    ]
    TOTAL, RUN = 8.0, 5.0
    x0, gap, cy = 90, 136, 112
    xs = [x0 + i * gap for i in range(len(stages))]
    xe = xs[-1]

    nodes = []
    for i, (icon, name, sub) in enumerate(stages):
        x = xs[i]
        ti = RUN * i / (len(stages) - 1)
        k = kt([0, ti, TOTAL - 0.5, TOTAL], TOTAL)
        nodes.append(
            f'<circle cx="{x}" cy="{cy}" r="30" fill="url(#acc)" opacity="0" filter="url(#soft)">'
            f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="0;.55;0;0" keyTimes="{k}"/></circle>'
            f'<circle cx="{x}" cy="{cy}" r="26" fill="{t["node"]}" stroke="{t["track"]}" stroke-width="2.5">'
            f'<animate attributeName="stroke" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{t["track"]};{t["acc2"]};{t["track"]};{t["track"]}" keyTimes="{k}"/></circle>'
            f'<text x="{x}" y="{cy + 6}" text-anchor="middle" font-size="17" font-weight="700" fill="{t["dim"]}">{escape(icon)}'
            f'<animate attributeName="fill" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{t["dim"]};{t["text"]};{t["dim"]};{t["dim"]}" keyTimes="{k}"/></text>'
            f'<text x="{x}" y="{cy + 56}" text-anchor="middle" font-size="15" font-weight="700" fill="{t["text"]}">{name}</text>'
            f'<text x="{x}" y="{cy + 76}" text-anchor="middle" font-size="12" fill="{t["dim"]}">{escape(sub)}</text>'
        )

    kr = kt([0, RUN, TOTAL - 0.5, TOTAL], TOTAL)
    kp = kt([0, RUN, RUN + 0.01, TOTAL - 0.5, TOTAL], TOTAL)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Pipeline animado: Plan, Code, Build, Test, Deploy, Monitor">
<defs>
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{t["acc1"]}"/><stop offset=".5" stop-color="{t["acc2"]}"/><stop offset="1" stop-color="{t["acc3"]}"/></linearGradient>
<linearGradient id="prog" gradientUnits="userSpaceOnUse" x1="{x0}" x2="{xe}"><stop offset="0" stop-color="{t["acc1"]}"/><stop offset=".5" stop-color="{t["acc2"]}"/><stop offset="1" stop-color="{t["acc3"]}"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{t["bg2"]}" stroke="{t["border"]}"/>
<g font-family="{FONT}">
<text x="26" y="36" font-size="13" fill="{t["dim"]}"><tspan fill="{t["acc2"]}">●</tspan>  pipeline <tspan fill="{t["text"]}" font-weight="700">marcela/carrera</tspan>  ·  main  ·  5+ años en producción</text>
<g font-size="13" font-weight="700">
<text x="{W - 26}" y="36" text-anchor="end" fill="{t["dim"]}">◌ running…<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="1;0;1" keyTimes="{kt([0, RUN, TOTAL - 0.5], TOTAL)}"/></text>
<text x="{W - 26}" y="36" text-anchor="end" fill="{t["ok"]}" opacity="0">✔ passed<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" values="0;1;0" keyTimes="{kt([0, RUN, TOTAL - 0.5], TOTAL)}"/></text>
</g>
<line x1="{x0}" y1="{cy}" x2="{xe}" y2="{cy}" stroke="{t["track"]}" stroke-width="3" stroke-dasharray="6 6"/>
<rect x="{x0}" y="{cy - 2}" height="4" width="0" rx="2" fill="url(#prog)">
<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" values="0;{xe - x0};{xe - x0};0" keyTimes="{kr}"/></rect>
{chr(10).join(nodes)}
<g>
<circle r="12" fill="{t["acc1"]}" filter="url(#soft)"/>
<circle r="6" fill="{t["acc1"]}"/>
<animateTransform attributeName="transform" type="translate" dur="{TOTAL}s" repeatCount="indefinite"
 values="{x0} {cy};{xe} {cy};{xe} {cy};{xe} {cy};{x0} {cy}" keyTimes="{kp}"/>
<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" values="1;1;0;0;0" keyTimes="{kp}"/>
</g>
</g>
</svg>
'''


for name, th in THEMES.items():
    (OUT / f"terminal-{name}.svg").write_text(terminal(th), encoding="utf-8")
    (OUT / f"pipeline-{name}.svg").write_text(pipeline(th), encoding="utf-8")
print("ok", sorted(p.name for p in OUT.iterdir()))
