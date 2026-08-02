#!/usr/bin/env python3
"""Build the playful, repository-native DEV ARCADE quest cards.

The SVGs are deterministic, self-hosted and dependency-free. Each project gets
its own small animated scene plus a separately composed mobile variant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "conf" / "projects.json"
OUT = ROOT / "assets" / "arcade" / "projects"
MONO = '"SFMono-Regular","Cascadia Code",Consolas,"Liberation Mono",Menlo,monospace'
SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif'

PALETTES = {
    "WEB": ("#32F5C4", "#4DA3FF"),
    "SOCIAL": ("#4DA3FF", "#FF4ECD"),
    "CACHE": ("#32F5C4", "#FFD166"),
    "BOT": ("#FFD166", "#FF6B6B"),
    "RAG": ("#4DA3FF", "#32F5C4"),
    "TOOL": ("#FF4ECD", "#4DA3FF"),
}

ROLE = {
    "WEB": "DESIGN + FRONTEND",
    "SOCIAL": "PRODUCT + FULL STACK",
    "CACHE": "BACKEND + SYSTEMS",
    "BOT": "AUTOMATION + DATA",
    "RAG": "SEARCH + AI SYSTEMS",
    "TOOL": "TOOLING + UX",
}


def tags(project: dict[str, object], x: int, y: int, mobile: bool = False) -> str:
    result: list[str] = []
    gap = 9 if mobile else 8
    for value in project["tags"]:
        value = str(value)
        char = 7.0 if mobile else 6.5
        width = max(70 if mobile else 60, 24 + len(value) * char)
        result.append(
            f'<g transform="translate({x:.1f} {y})"><rect class="pill" width="{width:.1f}" '
            f'height="{30 if mobile else 25}" rx="{15 if mobile else 12.5}"/>'
            f'<text class="pill-t" x="{width / 2:.1f}" y="{20 if mobile else 17}" '
            f'text-anchor="middle">{escape(value)}</text></g>'
        )
        x += width + gap
    return "".join(result)


def scene(kind: str, accent: str, accent2: str) -> str:
    """Return a 300 x 150 scene centered around (0, 0)."""
    if kind == "WEB":
        return f"""
<g class="scene">
  <rect class="screen" x="-142" y="-70" width="284" height="140" rx="10"/>
  <path class="dim" d="M-142-42h284"/><circle cx="-124" cy="-56" r="4" fill="#FF6B6B"/><circle cx="-110" cy="-56" r="4" fill="#FFD166"/><circle cx="-96" cy="-56" r="4" fill="{accent}"/>
  <rect class="soft a1" x="-121" y="-20" width="88" height="56" rx="6"/><rect class="soft2 a2" x="-19" y="-20" width="137" height="15" rx="4"/><rect class="soft a3" x="-19" y="7" width="61" height="29" rx="4"/><rect class="soft a4" x="54" y="7" width="64" height="29" rx="4"/>
  <g class="cursor"><path d="M-2-5v27l8-8 7 14 7-4-7-14h12z" fill="{accent2}" stroke="#080B12" stroke-width="2"/></g>
  <text class="scene-t" x="0" y="58" text-anchor="middle">LAYOUT → MOTION → RESPONSIVE</text>
</g>"""
    if kind == "SOCIAL":
        return f"""
<g class="scene">
  <path class="route" d="M-105 27Q-55-70 0-18T105 27"/>
  <g transform="translate(-105 27)"><g class="avatar av1"><circle r="25"/><circle cy="-7" r="7"/><path d="M-13 12q13-18 26 0"/></g></g>
  <g transform="translate(0 -18)"><g class="avatar av2"><circle r="29"/><circle cy="-8" r="8"/><path d="M-15 14q15-21 30 0"/></g></g>
  <g transform="translate(105 27)"><g class="avatar av3"><circle r="25"/><circle cy="-7" r="7"/><path d="M-13 12q13-18 26 0"/></g></g>
  <g class="bubble b1"><rect x="-84" y="-62" width="52" height="29" rx="8"/><path d="M-72-33l-5 9 14-9"/><text x="-58" y="-43" text-anchor="middle">+1</text></g>
  <g class="bubble b2"><rect x="52" y="-57" width="60" height="29" rx="8"/><path d="M66-28l-5 9 14-9"/><text x="82" y="-38" text-anchor="middle">♥</text></g>
  <text class="scene-t" x="0" y="72" text-anchor="middle">DISCOVER · TRACK · DISCUSS</text>
</g>"""
    if kind == "CACHE":
        return f"""
<g class="scene">
  <rect class="screen" x="-142" y="-65" width="284" height="130" rx="10"/>
  <g transform="translate(62 -5)"><ellipse class="soft" rx="46" ry="14"/><path class="accent-stroke" d="M-46 0v25c0 8 21 14 46 14s46-6 46-14V0M-46 24v25c0 8 21 14 46 14s46-6 46-14V24"/><text class="scene-t" x="0" y="9" text-anchor="middle">CACHE</text></g>
  <g class="packet p1"><rect width="35" height="18" rx="4"/><text x="17.5" y="13" text-anchor="middle">01</text></g>
  <g class="packet p2"><rect width="35" height="18" rx="4"/><text x="17.5" y="13" text-anchor="middle">{{ }}</text></g>
  <g class="packet p3"><rect width="35" height="18" rx="4"/><text x="17.5" y="13" text-anchor="middle">AI</text></g>
  <path class="route" d="M-70-30h57v59h28"/><circle class="hit" cx="6" cy="29" r="7" fill="{accent2}"/><text class="scene-t" x="-66" y="57">STREAM SAFE</text>
</g>"""
    if kind == "BOT":
        return f"""
<g class="scene">
  <path class="belt" d="M-142 35H142"/><g class="rollers"><circle cx="-115" cy="35" r="10"/><circle cx="-62" cy="35" r="10"/><circle cx="-9" cy="35" r="10"/><circle cx="44" cy="35" r="10"/><circle cx="97" cy="35" r="10"/></g>
  <g class="box bx1"><rect x="-20" y="-24" width="40" height="32" rx="4"/><text x="0" y="-3" text-anchor="middle">₺</text></g>
  <g class="box bx2"><rect x="-20" y="-24" width="40" height="32" rx="4"/><text x="0" y="-3" text-anchor="middle">$</text></g>
  <g class="alert"><path d="M91-62h43v48H91z"/><path d="M101-51h23M101-42h18M101-33h12"/><circle cx="128" cy="-18" r="10" fill="{accent2}"/><text x="128" y="-14" text-anchor="middle">!</text></g>
  <path class="scanline" d="M63-54v76"/><text class="scene-t" x="0" y="69" text-anchor="middle">WATCH → COMPARE → ALERT</text>
</g>"""
    if kind == "RAG":
        return f"""
<g class="scene">
  <g class="query"><rect x="-137" y="-18" width="72" height="36" rx="8"/><text x="-101" y="5" text-anchor="middle">QUERY</text></g>
  <path class="route" d="M-65 0H-32M32 0h33M92-35l-27 35 27 35"/>
  <g class="core"><circle r="32"/><text y="5" text-anchor="middle">RRF</text></g>
  <g class="node n1" transform="translate(106 -39)"><circle r="22"/><text y="4" text-anchor="middle">D</text></g><g class="node n2" transform="translate(106 0)"><circle r="22"/><text y="4" text-anchor="middle">B</text></g><g class="node n3" transform="translate(106 39)"><circle r="22"/><text y="4" text-anchor="middle">✓</text></g>
  <text class="scene-t" x="0" y="72" text-anchor="middle">RETRIEVE · RERANK · VERIFY</text>
</g>"""
    return f"""
<g class="scene">
  <g class="flow f1" transform="translate(-126 -43)"><rect width="66" height="30" rx="6"/><text x="33" y="20" text-anchor="middle">TRIGGER</text></g>
  <g class="flow f2" transform="translate(-126 9)"><rect width="66" height="30" rx="6"/><text x="33" y="20" text-anchor="middle">ACTION</text></g>
  <path class="route" d="M-60-28h38v52h25"/>
  <g transform="translate(22 10)"><g class="gear"><circle r="31"/><path d="M-9 0h18M0-9v18"/></g></g>
  <path class="route" d="M53 10h25"/>
  <g class="codeout" transform="translate(79 -42)"><rect width="62" height="103" rx="7"/><path d="M13 24h34M13 40h25M13 56h34M13 72h20"/><text x="31" y="94" text-anchor="middle">.PY</text></g>
  <text class="scene-t" x="0" y="76" text-anchor="middle">WORKFLOW → READABLE CODE</text>
</g>"""


def base_style(accent: str, accent2: str, mobile: bool = False) -> str:
    return f"""
text{{font-family:{MONO}}}.panel{{fill:url(#panel)}}.grid{{fill:url(#grid)}}.border{{fill:none;stroke:url(#edge);stroke-width:1.25}}
.sans{{font-family:{SANS}}}.micro{{font-size:{16 if mobile else 9}px;font-weight:750;letter-spacing:{1 if mobile else 1.25}px;fill:#82909C}}.quest{{font-size:{18 if mobile else 10}px;font-weight:850;letter-spacing:{1 if mobile else 1.4}px;fill:{accent}}}
.title{{font-size:{36 if mobile else 25}px;font-weight:850;letter-spacing:.3px;fill:#EDF6FF}}.body{{font-size:{20 if mobile else 13}px;font-weight:450;fill:#A8B4C0}}.role{{font-size:{17 if mobile else 9}px;font-weight:750;letter-spacing:{.7 if mobile else 1}px;fill:#C8D3DD}}
.pill{{fill:{accent};fill-opacity:.08;stroke:{accent};stroke-opacity:.35}}.pill-t{{font-size:{15 if mobile else 9}px;font-weight:700;fill:#CBD6DF}}.status{{fill:{accent};fill-opacity:.12;stroke:{accent};stroke-opacity:.65}}.status-t{{font-size:{15 if mobile else 9}px;font-weight:850;letter-spacing:{.7 if mobile else 1}px;fill:{accent}}}
.screen{{fill:#080D16;stroke:#334155}}.soft{{fill:{accent};fill-opacity:.16;stroke:{accent}}}.soft2{{fill:{accent2};fill-opacity:.16;stroke:{accent2}}}.dim,.accent-stroke{{fill:none;stroke:#3A4A5D;stroke-width:2}}.accent-stroke{{stroke:{accent}}}.route{{fill:none;stroke:{accent};stroke-width:2;stroke-dasharray:6 6;animation:route 2.4s linear infinite}}
.scene-t{{font-size:{11 if mobile else 8}px;font-weight:750;letter-spacing:{.7 if mobile else 1}px;fill:#95A3B0}}.cursor{{animation:cursor 4.8s ease-in-out infinite}}.a1{{animation:pop 4.8s .15s ease-in-out infinite}}.a2{{animation:pop 4.8s .4s ease-in-out infinite}}.a3{{animation:pop 4.8s .65s ease-in-out infinite}}.a4{{animation:pop 4.8s .9s ease-in-out infinite}}
.avatar circle,.avatar path,.node circle,.core circle{{fill:#101B28;stroke:{accent};stroke-width:2}}.avatar path{{fill:none}}.av1{{animation:bob 3s ease-in-out infinite}}.av2{{animation:bob 3s .4s ease-in-out infinite}}.av3{{animation:bob 3s .8s ease-in-out infinite}}.bubble rect,.bubble path{{fill:#111927;stroke:{accent2}}}.bubble text,.query text,.core text,.node text,.flow text,.codeout text,.box text,.alert text{{font-size:{11 if mobile else 9}px;font-weight:850;fill:#EDF6FF}}.b1{{animation:chat 4s ease-in-out infinite}}.b2{{animation:chat 4s 1.5s ease-in-out infinite}}
.packet rect,.query rect,.flow rect,.codeout rect,.box rect,.alert path{{fill:#111927;stroke:{accent};stroke-width:2}}.packet{{transform:translate(-113px,-39px)}}.packet text{{font-size:{10 if mobile else 8}px;font-weight:850;fill:#EDF6FF}}.p1{{animation:packet 4.8s linear infinite}}.p2{{animation:packet 4.8s 1.2s linear infinite}}.p3{{animation:packet 4.8s 2.4s linear infinite}}.hit{{animation:hit 1.4s ease-in-out infinite}}
.belt{{stroke:#465466;stroke-width:8}}.rollers circle{{fill:#101824;stroke:{accent}}}.box{{transform:translate(-145px,4px);animation:box 5s linear infinite}}.bx2{{animation-delay:-2.5s}}.alert{{animation:alert 2s ease-in-out infinite}}.scanline{{stroke:{accent2};stroke-width:3;animation:scanline 3s ease-in-out infinite}}
.query{{animation:query 4s ease-in-out infinite}}.core{{animation:core 2.8s ease-in-out infinite}}.node circle{{stroke:{accent2}}}.n1{{animation:pick 4.2s ease-in-out infinite}}.n2{{animation:pick 4.2s 1.1s ease-in-out infinite}}.n3{{animation:pick 4.2s 2.2s ease-in-out infinite}}
.flow rect,.codeout rect{{stroke:{accent2}}}.gear circle,.gear path{{fill:#111927;stroke:{accent};stroke-width:2}}.gear{{animation:spin 7s linear infinite}}.f1{{animation:flow 4s ease-in-out infinite}}.f2{{animation:flow 4s .9s ease-in-out infinite}}
.progress{{fill:#14202B}}.progress-in{{fill:{accent};animation:progress 6s ease-in-out infinite}}
@keyframes route{{to{{stroke-dashoffset:-24}}}}@keyframes cursor{{0%,15%{{transform:translate(-105px,36px)}}38%{{transform:translate(-20px,-5px)}}62%{{transform:translate(54px,23px)}}85%,100%{{transform:translate(102px,-31px)}}}}@keyframes pop{{0%,12%{{opacity:.18;transform:translateY(5px)}}24%,100%{{opacity:1;transform:none}}}}@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}@keyframes chat{{0%,20%,100%{{opacity:0;transform:translateY(7px)}}30%,72%{{opacity:1;transform:none}}}}@keyframes packet{{0%{{transform:translate(-113px,-39px);opacity:0}}12%{{opacity:1}}72%{{transform:translate(44px,30px);opacity:1}}85%,100%{{transform:translate(74px,30px);opacity:0}}}}@keyframes hit{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes box{{from{{transform:translate(-145px,4px)}}to{{transform:translate(145px,4px)}}}}@keyframes alert{{0%,35%,100%{{opacity:.3;transform:translateY(4px)}}45%,72%{{opacity:1;transform:none}}}}@keyframes scanline{{0%,100%{{transform:translateX(-80px);opacity:.1}}50%{{transform:translateX(72px);opacity:1}}}}@keyframes query{{0%,15%{{transform:translateX(-15px);opacity:.4}}35%,100%{{transform:none;opacity:1}}}}@keyframes core{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}@keyframes pick{{0%,20%,100%{{opacity:.35}}35%,60%{{opacity:1}}}}@keyframes spin{{to{{transform:rotate(360deg)}}}}@keyframes flow{{0%,20%{{opacity:.3}}35%,70%{{opacity:1}}100%{{opacity:.3}}}}@keyframes progress{{0%{{width:20px}}55%,100%{{width:96%}}}}
@media(prefers-color-scheme:light){{.panel{{fill:#F6F8FA}}.title{{fill:#172033}}.body,.micro,.scene-t{{fill:#596879}}.role,.pill-t{{fill:#334155}}.screen{{fill:#FFFFFF}}.avatar circle,.core circle,.node circle,.gear circle,.gear path,.packet rect,.query rect,.flow rect,.codeout rect,.box rect,.alert path,.bubble rect,.bubble path{{fill:#FFFFFF}}.bubble text,.query text,.core text,.node text,.flow text,.codeout text,.box text,.alert text,.packet text{{fill:#172033}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def render(project: dict[str, object]) -> str:
    kind = str(project["glyph"])
    accent, accent2 = PALETTES.get(kind, ("#32F5C4", "#4DA3FF"))
    title = escape(str(project["title"]))
    desc = [escape(str(v)) for v in project["description"]]
    signal = escape(str(project["signal"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Quest {project['id']}: {title}. {desc[0]} {desc[1]}">
<title>Quest {project['id']} — {title}</title><desc>{desc[0]} {desc[1]}</desc>
<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#070A11"/></linearGradient><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{accent}"/><stop offset="1" stop-color="{accent2}"/></linearGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{accent}" stroke-opacity=".045"/></pattern></defs>
<style>{base_style(accent, accent2)}</style>
<rect class="panel" x="1" y="1" width="998" height="258" rx="16"/><rect class="grid" x="1" y="1" width="998" height="258" rx="16"/><rect class="border" x="1" y="1" width="998" height="258" rx="16"/>
<path d="M620 24v212" stroke="#334155"/><text class="quest" x="28" y="34">QUEST {project['id']} / {escape(str(project['eyebrow']))}</text><g transform="translate(493 17)"><rect class="status" width="104" height="25" rx="12.5"/><text class="status-t" x="52" y="17" text-anchor="middle">● {signal}</text></g>
<text class="title sans" x="28" y="76">{title}</text><text class="body sans" x="28" y="108">{desc[0]}</text><text class="body sans" x="28" y="129">{desc[1]}</text><text class="micro" x="28" y="166">PLAYER ROLE</text><text class="role" x="136" y="166">{ROLE.get(kind, 'BUILD + SHIP')}</text>{tags(project, 28, 184)}
<rect class="progress" x="28" y="231" width="568" height="7" rx="3.5"/><rect class="progress-in" x="28" y="231" width="546" height="7" rx="3.5"/><text class="micro" x="596" y="217" text-anchor="end">QUEST COMPLETE ✓</text>
<g transform="translate(807 130)">{scene(kind, accent, accent2)}</g>
</svg>"""


def render_mobile(project: dict[str, object]) -> str:
    kind = str(project["glyph"])
    accent, accent2 = PALETTES.get(kind, ("#32F5C4", "#4DA3FF"))
    title = escape(str(project["title"]))
    desc = [escape(str(v)) for v in project["description"]]
    signal = escape(str(project["signal"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 560" role="img" aria-label="Quest {project['id']}: {title}. {desc[0]} {desc[1]}">
<title>Quest {project['id']} — {title} mobile</title><desc>{desc[0]} {desc[1]}</desc>
<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#070A11"/></linearGradient><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{accent}"/><stop offset="1" stop-color="{accent2}"/></linearGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{accent}" stroke-opacity=".045"/></pattern></defs>
<style>{base_style(accent, accent2, True)}</style>
<rect class="panel" x="1" y="1" width="718" height="558" rx="20"/><rect class="grid" x="1" y="1" width="718" height="558" rx="20"/><rect class="border" x="1" y="1" width="718" height="558" rx="20"/>
<text class="quest" x="32" y="44">QUEST {project['id']} / {escape(str(project['eyebrow']))}</text><g transform="translate(532 22)"><rect class="status" width="156" height="35" rx="17.5"/><text class="status-t" x="78" y="23" text-anchor="middle">● {signal}</text></g>
<text class="title sans" x="32" y="99">{title}</text><text class="body sans" x="32" y="137">{desc[0]}</text><text class="body sans" x="32" y="165">{desc[1]}</text><text class="micro" x="32" y="207">PLAYER ROLE</text><text class="role" x="185" y="207">{ROLE.get(kind, 'BUILD + SHIP')}</text>{tags(project, 32, 226, True)}
<path d="M32 279H688" stroke="#334155"/><g transform="translate(360 390) scale(1.55)">{scene(kind, accent, accent2)}</g>
<rect class="progress" x="32" y="532" width="656" height="8" rx="4"/><rect class="progress-in" x="32" y="532" width="630" height="8" rx="4"/>
</svg>"""


def load() -> list[dict[str, object]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("conf/projects.json must be a non-empty list")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    expected: set[str] = set()
    for project in load():
        variants = {
            f"{project['slug']}-quest-v1.svg": render(project),
            f"{project['slug']}-quest-mobile-v1.svg": render_mobile(project),
        }
        expected.update(variants)
        for name, source in variants.items():
            path = OUT / name
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != source:
                    stale.append(name)
            else:
                path.write_text(source, encoding="utf-8")
                print(f"[ok] wrote {path.relative_to(ROOT)}")
    extra = {p.name for p in OUT.glob("*.svg")} - expected
    if stale or (args.check and extra):
        if stale:
            print(f"[error] stale/missing arcade cards: {', '.join(stale)}", file=sys.stderr)
        if extra:
            print(f"[error] unconfigured arcade cards: {', '.join(sorted(extra))}", file=sys.stderr)
        return 1
    if args.check:
        print(f"[ok] {len(expected)} arcade project cards are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
