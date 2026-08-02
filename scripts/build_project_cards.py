#!/usr/bin/env python3
"""Render deterministic, theme-aware SVG cards for the profile README.

The cards intentionally have no runtime or external-service dependency. Run:

    python scripts/build_project_cards.py
    python scripts/build_project_cards.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "conf" / "projects.json"
OUT_DIR = ROOT / "assets" / "projects"
MONO = '"SFMono-Regular", "Cascadia Code", Consolas, "Liberation Mono", Menlo, monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, Roboto, sans-serif'


def pill(x: int, y: int, label: str, index: int) -> tuple[str, int]:
    width = max(58, 18 + len(label) * 7)
    return (
        f'<g transform="translate({x} {y})">'
        f'<rect class="pill" width="{width}" height="24" rx="12"/>'
        f'<text class="pill-text" x="{width / 2:.1f}" y="16" text-anchor="middle">'
        f'{escape(label)}</text></g>',
        x + width + (8 if index < 2 else 0),
    )


def mobile_pill(x: int, y: int, label: str, index: int) -> tuple[str, int]:
    width = max(52, 16 + len(label) * 6)
    return (
        f'<g transform="translate({x} {y})">'
        f'<rect class="pill" width="{width}" height="27" rx="13.5"/>'
        f'<text class="pill-text" x="{width / 2:.1f}" y="18" text-anchor="middle">'
        f'{escape(label)}</text></g>',
        x + width + (7 if index < 2 else 0),
    )


def glyph(kind: str, accent: str, accent2: str, x: int = 438, y: int = 100) -> str:
    shared = f'stroke="{accent}" stroke-width="1.7" fill="none"'
    if kind == "WEB":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <rect x="-48" y="-36" width="96" height="72" rx="10"/>
          <path d="M-48-17h96M-36-27h2M-27-27h2M-18-27h2" opacity=".65"/>
          <path d="M-30 16c10-25 21 25 31 0s21 25 31 0"/>
          <circle class="orb" cx="32" cy="16" r="4.5" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "SOCIAL":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <circle cx="0" cy="-28" r="12"/><circle cx="-34" cy="3" r="9"/><circle cx="34" cy="3" r="9"/>
          <path d="M-22 39c2-17 10-25 22-25s20 8 22 25M-48 32c1-12 6-18 14-18 5 0 9 2 12 7M48 32c-1-12-6-18-14-18-5 0-9 2-12 7"/>
          <circle class="orb" cx="0" cy="-28" r="4" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "CACHE":
        return f"""
        <g transform="translate({x} {y - 22})" {shared}>
          <ellipse rx="34" ry="11"/><path d="M-34 0v18c0 6 15 11 34 11s34-5 34-11V0"/>
          <path d="M-34 18v18c0 6 15 11 34 11s34-5 34-11V18" opacity=".65"/>
          <circle class="orb" cx="0" cy="-24" r="4" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "RAG":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M-42-20L0-43 42-20 0 3Z"/><path d="M-42 0L0 23 42 0M-42 20L0 43 42 20" opacity=".62"/>
          <circle class="orb" cx="0" cy="3" r="5" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "ROUTE":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M-46 0H-12M12-28H34l12 12M12 0h34M12 28H34l12-12"/>
          <rect x="-12" y="-12" width="24" height="24" rx="6"/>
          <circle class="orb" cx="46" cy="0" r="5" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "TRACE":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M-48 10h17l10-35 17 58 13-44 10 21h29"/>
          <circle class="orb" cx="-21" cy="-25" r="4.5" fill="{accent2}" stroke="none"/>
          <circle cx="9" cy="-11" r="4"/>
        </g>"""
    if kind == "BOT":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M0-43v12M-11-43h22M-35-27h70a8 8 0 018 8v48a8 8 0 01-8 8h-70a8 8 0 01-8-8v-48a8 8 0 018-8z"/>
          <circle cx="-18" cy="1" r="5"/><circle cx="18" cy="1" r="5"/><path d="M-18 21h36M-51-9v28M51-9v28" opacity=".65"/>
          <circle class="orb" cx="0" cy="-43" r="4" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "TOOL":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M-43-34h-12v68h12M43-34h12v68H43M-29 18l18-36M2-18l18 18-18 18"/>
          <circle class="orb" cx="20" cy="0" r="4.5" fill="{accent2}" stroke="none"/>
        </g>"""
    if kind == "DOC":
        return f"""
        <g transform="translate({x} {y})" {shared}>
          <path d="M-28-43h38l20 20v66h-58z"/><path d="M10-43v20h20M-14-5h29M-14 9h29M-14 23h20" opacity=".65"/>
          <circle class="orb" cx="30" cy="-23" r="4.5" fill="{accent2}" stroke="none"/>
        </g>"""
    return f"""
      <g transform="translate({x} {y})" {shared}>
        <circle cx="-38" cy="-22" r="10"/><circle cx="38" cy="-22" r="10"/>
        <circle cx="0" cy="34" r="10"/><path d="M-29-15L-6 25M29-15L6 25M-28-22h56"/>
        <circle class="orb" cx="0" cy="-22" r="5" fill="{accent2}" stroke="none"/>
      </g>"""


def render_card(project: dict[str, object]) -> str:
    accent = str(project["accent"])
    accent2 = str(project["accent2"])
    title = escape(str(project["title"]))
    eyebrow = escape(str(project["eyebrow"]))
    signal = escape(str(project["signal"]))
    descriptions = [escape(str(line)) for line in project["description"]]

    tags: list[str] = [str(tag) for tag in project["tags"]]
    tag_parts: list[str] = []
    x = 26
    for i, tag in enumerate(tags):
        part, x = pill(x, 142, tag, i)
        tag_parts.append(part)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 180" role="img" aria-label="{title}: {descriptions[0]} {descriptions[1]}">
  <title>{title}</title>
  <desc>{descriptions[0]} {descriptions[1]}</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#101720"/><stop offset="1" stop-color="#080D14"/>
    </linearGradient>
    <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="520" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="{accent}" stop-opacity=".08"/>
      <stop offset=".5" stop-color="{accent}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{accent2}" stop-opacity=".12"/>
    </linearGradient>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" fill="none" stroke="{accent}" stroke-opacity=".035"/>
    </pattern>
    <filter id="glow" x="-250%" y="-250%" width="600%" height="600%"><feGaussianBlur stdDeviation="4"/></filter>
  </defs>
  <style>
    .panel{{fill:url(#panel)}} .edge{{fill:none;stroke:url(#edge);stroke-width:1.25}}
    .grid{{fill:url(#grid)}} .title{{font:700 20px {SANS};letter-spacing:.4px;fill:#E6EDF3}}
    .eye{{font:600 9.5px {MONO};letter-spacing:1.7px;fill:{accent}}}
    .body{{font:400 12.5px {SANS};fill:#9DA7B3}}
    .num{{font:600 10px {MONO};fill:{accent}}} .signal{{font:600 9px {MONO};letter-spacing:1px;fill:#9DA7B3}}
    .pill{{fill:{accent};fill-opacity:.075;stroke:{accent};stroke-opacity:.24}}
    .pill-text{{font:600 9.5px {MONO};fill:#B9C3CE}}
    .orb{{animation:pulse 2.8s ease-in-out infinite}} .scan{{animation:scan 5s ease-in-out infinite}}
    @keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
    @keyframes scan{{0%,12%{{transform:translateX(-520px);opacity:0}}35%,65%{{opacity:.55}}88%,100%{{transform:translateX(520px);opacity:0}}}}
    @media (prefers-color-scheme:light){{
      .panel{{fill:#F6F8FA}} .title{{fill:#1F2328}} .body,.signal{{fill:#57606A}}
      .pill-text{{fill:#3F4852}} .grid{{opacity:.45}}
    }}
    @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  </style>
  <rect class="panel" x="1" y="1" width="518" height="178" rx="14"/>
  <rect class="grid" x="1" y="1" width="518" height="178" rx="14"/>
  <rect class="edge" x="1" y="1" width="518" height="178" rx="14"/>
  <rect class="scan" x="-120" y="1" width="120" height="178" fill="{accent}" opacity="0"/>
  <text class="num" x="26" y="28">// {escape(str(project['id']))}</text>
  <circle cx="394" cy="24" r="3" fill="{accent}"/><circle cx="394" cy="24" r="8" fill="{accent}" opacity=".14" filter="url(#glow)"/>
  <text class="signal" x="404" y="28">{signal}</text>
  <text class="eye" x="26" y="51">{eyebrow}</text>
  <text class="title" x="26" y="80">{title}</text>
  <text class="body" x="26" y="105">{descriptions[0]}</text>
  <text class="body" x="26" y="123">{descriptions[1]}</text>
  {''.join(tag_parts)}
  {glyph(str(project['glyph']), accent, accent2).lstrip()}
</svg>
"""


def render_mobile_card(project: dict[str, object]) -> str:
    accent = str(project["accent"])
    accent2 = str(project["accent2"])
    title = escape(str(project["title"]))
    eyebrow = escape(str(project["eyebrow"]))
    signal = escape(str(project["signal"]))
    descriptions = [escape(str(line)) for line in project["description"]]

    tag_parts: list[str] = []
    x = 20
    for index, tag in enumerate(str(value) for value in project["tags"]):
        part, x = mobile_pill(x, 171, tag, index)
        tag_parts.append(part)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 218" role="img" aria-label="{title}: {descriptions[0]} {descriptions[1]}">
  <title>{title}</title>
  <desc>{descriptions[0]} {descriptions[1]}</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#101720"/><stop offset="1" stop-color="#080D14"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{accent}"/><stop offset="1" stop-color="{accent2}"/></linearGradient>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{accent}" stroke-opacity=".035"/></pattern>
    <filter id="glow" x="-250%" y="-250%" width="600%" height="600%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>
  <style>
    .panel{{fill:url(#panel)}}.edge{{fill:none;stroke:url(#edge)}}.grid{{fill:url(#grid)}}
    .title{{font:700 18px {SANS};letter-spacing:.2px;fill:#E6EDF3}}.eye{{font:650 8px {MONO};letter-spacing:1.25px;fill:{accent}}}
    .body{{font:400 11.5px {SANS};fill:#9DA7B3}}.num{{font:650 8px {MONO};fill:{accent}}}.signal{{font:650 7.5px {MONO};letter-spacing:.8px;fill:#9DA7B3}}
    .pill{{fill:{accent};fill-opacity:.075;stroke:{accent};stroke-opacity:.26}}.pill-text{{font:650 8.5px {MONO};fill:#B9C3CE}}
    .orb{{animation:pulse 2.8s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
    @media(prefers-color-scheme:light){{.panel{{fill:#F6F8FA}}.title{{fill:#1F2328}}.body,.signal{{fill:#57606A}}.pill-text{{fill:#3F4852}}.grid{{opacity:.45}}}}
    @media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  </style>
  <rect class="panel" x="1" y="1" width="358" height="216" rx="14"/><rect class="grid" x="1" y="1" width="358" height="216" rx="14"/><rect class="edge" x="1" y="1" width="358" height="216" rx="14"/>
  <text class="num" x="20" y="24">// {escape(str(project['id']))}</text><circle cx="246" cy="21" r="2.5" fill="{accent}"/><circle cx="246" cy="21" r="7" fill="{accent}" opacity=".14" filter="url(#glow)"/><text class="signal" x="254" y="24">{signal}</text>
  <text class="eye" x="20" y="52">{eyebrow}</text><text class="title" x="20" y="81">{title}</text>
  <text class="body" x="20" y="112">{descriptions[0]}</text><text class="body" x="20" y="130">{descriptions[1]}</text>
  <path d="M20 151H340" stroke="{accent}" stroke-opacity=".15"/>{''.join(tag_parts)}
  {glyph(str(project['glyph']), accent, accent2, 296, 103).lstrip()}
</svg>
"""


def load_projects() -> list[dict[str, object]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("conf/projects.json must contain a non-empty list")
    slugs: set[str] = set()
    for item in data:
        required = {"id", "slug", "title", "eyebrow", "description", "tags", "signal", "accent", "accent2", "glyph"}
        missing = required.difference(item)
        if missing:
            raise ValueError(f"{item.get('slug', '<unknown>')}: missing {sorted(missing)}")
        slug = str(item["slug"])
        if slug in slugs:
            raise ValueError(f"duplicate slug: {slug}")
        slugs.add(slug)
        if len(item["description"]) != 2 or len(item["tags"]) != 3:
            raise ValueError(f"{slug}: exactly two description lines and three tags are required")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed cards differ")
    args = parser.parse_args()

    projects = load_projects()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    expected = {
        name
        for project in projects
        for name in (f"{project['slug']}.svg", f"{project['slug']}-mobile.svg")
    }

    for project in projects:
        variants = {
            f"{project['slug']}.svg": render_card(project),
            f"{project['slug']}-mobile.svg": render_mobile_card(project),
        }
        for name, rendered in variants.items():
            path = OUT_DIR / name
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                    stale.append(path.name)
            else:
                path.write_text(rendered, encoding="utf-8")
                print(f"[ok] wrote {path.relative_to(ROOT)}")

    extra = {path.name for path in OUT_DIR.glob("*.svg")}.difference(expected)
    if args.check and (stale or extra):
        if stale:
            print(f"[error] stale/missing cards: {', '.join(stale)}", file=sys.stderr)
        if extra:
            print(f"[error] unconfigured cards: {', '.join(sorted(extra))}", file=sys.stderr)
        return 1
    if args.check:
        print(f"[ok] {len(projects)} project cards are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
