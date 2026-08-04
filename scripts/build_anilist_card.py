#!/usr/bin/env python3
"""Render the AniList panel from the raw list instead of AniList's own summary.

img.anili.st reads User.statistics, and on this account that aggregate is stuck
at zero: the list holds 25 completed entries with progress on 24 of them, yet
statistics.anime.count, episodesWatched and minutesWatched all report 0 and have
stayed there for more than eight hours. MediaListCollection returns the real
rows, so everything here is counted from those.

Output is a hand-written SVG in the README's palette, which the hosted card
never matched anyway. No <script>: it would not run inside the <img> GitHub
renders this in.
"""
from __future__ import annotations

import collections
import html
import json
import pathlib
import urllib.request

USER = "metmete"
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "anilist.svg"

BG = "#1a0b2e"
INK = "#f7e8ff"
PINK = "#FF6B9D"
PURPLE = "#C56CF0"
GOLD = "#FEC868"
ORANGE = "#FF9E64"
MUTED = "#9b7bb8"

GENRE_COLOURS = [PINK, PURPLE, GOLD, ORANGE, "#6BCBFF", "#8B7BF0"]

QUERY = """
query ($n: String) {
  MediaListCollection(userName: $n, type: ANIME) {
    lists { entries { status progress media { episodes duration genres } } } }
}
"""


def fetch() -> list[dict]:
    body = json.dumps({"query": QUERY, "variables": {"n": USER}}).encode()
    req = urllib.request.Request(
        "https://graphql.anilist.co", data=body,
        # AniList answers 403 to urllib's default User-Agent
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": "metehanulusoy-profile-readme/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"AniList returned errors: {payload['errors']}")
    lists = payload["data"]["MediaListCollection"]["lists"]
    return [entry for group in lists for entry in group["entries"]]


def summarise(entries: list[dict]) -> dict:
    finished = [e for e in entries if e["status"] == "COMPLETED"]
    episodes = 0
    minutes = 0
    for e in entries:
        media = e["media"]
        total = media["episodes"] or 0
        # a completed show counts in full; anything else counts what was watched
        watched = total if e["status"] == "COMPLETED" else min(e["progress"] or 0, total or 10**6)
        episodes += watched
        minutes += watched * (media["duration"] or 0)
    genres = collections.Counter(
        g for e in entries for g in (e["media"]["genres"] or []))
    return {
        "series": len(entries),
        "finished": len(finished),
        "episodes": episodes,
        "days": minutes / 1440,
        "genres": genres.most_common(4),
    }


def bar(stats: dict, x: float, y: float, width: float) -> str:
    top = stats["genres"]
    if not top:
        return ""
    total = sum(n for _, n in top)
    parts = []
    cursor = x
    for i, (_, n) in enumerate(top):
        w = width * n / total
        # a 1px gap keeps neighbouring segments from bleeding into each other
        parts.append(f'<rect x="{cursor:.1f}" y="{y}" width="{max(w - 1.5, 1):.1f}" '
                     f'height="7" rx="3.5" fill="{GENRE_COLOURS[i]}"/>')
        cursor += w
    for i, (name, _) in enumerate(top):
        col = i % 2
        row = i // 2
        lx = x + col * (width / 2)
        ly = y + 26 + row * 19
        parts.append(f'<circle cx="{lx + 4:.1f}" cy="{ly - 4:.1f}" r="4" fill="{GENRE_COLOURS[i]}"/>')
        parts.append(f'<text class="lg" x="{lx + 15:.1f}" y="{ly}">{html.escape(name)}</text>')
    return "".join(parts)


def render(stats: dict) -> str:
    rows = [
        ("Series completed", f"{stats['finished']}"),
        ("Episodes watched", f"{stats['episodes']:,}"),
        ("Days watched", f"{stats['days']:.1f}"),
    ]
    lines = []
    for i, (label, value) in enumerate(rows):
        y = 78 + i * 30
        lines.append(f'<text class="k" x="26" y="{y}">{label}</text>')
        lines.append(f'<text class="v" x="290" y="{y}">{value}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 250" role="img"
     aria-label="AniList: {stats['finished']} series completed, {stats['episodes']} episodes, {stats['days']:.1f} days">
  <style>
    .t{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
       font-size:19px;font-weight:800;fill:{PINK}}}
    .k{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
       font-size:14px;fill:{INK}}}
    .v{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
       font-size:14px;font-weight:700;fill:{INK}}}
    .lg{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
        font-size:12.5px;fill:{INK}}}
    .b{{font-family:"SFMono-Regular",Consolas,Menlo,monospace;font-size:10px;
       letter-spacing:2px;fill:{MUTED}}}
  </style>
  <rect width="500" height="250" rx="6" fill="{BG}"/>
  <text class="t" x="26" y="38">My Anime List</text>
  <text class="b" x="474" y="37" text-anchor="end">ANILIST</text>
  {''.join(lines)}
  {bar(stats, 26, 182, 448)}
</svg>
'''


def main() -> None:
    stats = summarise(fetch())
    OUT.write_text(render(stats), encoding="utf-8")
    print(f"wrote {OUT.name}: {stats['finished']} series, {stats['episodes']} episodes, "
          f"{stats['days']:.1f} days, genres {[g for g, _ in stats['genres']]}")


if __name__ == "__main__":
    main()
