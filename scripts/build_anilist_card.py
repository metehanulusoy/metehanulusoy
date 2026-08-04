#!/usr/bin/env python3
"""Render the AniList panel as a wall of cover art, drawn from the raw list.

Two reasons this is generated here rather than pulled from img.anili.st:

  * That service reads User.statistics, and on this account the aggregate is
    stuck at zero — the list holds completed entries with progress on them while
    count/episodesWatched/minutesWatched all report 0. MediaListCollection
    returns the real rows, so everything here is counted from those.
  * A panel of numbers did not show what the list actually is. The covers do.

The covers are embedded as base64 JPEGs. An SVG inside the <img> GitHub renders
this in is its own document and browsers block its external requests, so linking
s4.anilist.co would render an empty grid. Thumbnails are sized to keep the whole
file under the 120 KB ceiling validate_assets.py enforces.
"""
from __future__ import annotations

import base64
import concurrent.futures as cf
import html
import io
import json
import pathlib
import urllib.request

from PIL import Image

USER = "metmete"
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "anilist.svg"

BG = "#1a0b2e"
INK = "#f7e8ff"
PINK = "#FF6B9D"
MUTED = "#9b7bb8"

WIDTH = 1000
PAD = 24
PER_ROW = 13
GAP = 6
COVER_W = 66
COVER_H = 99
JPEG_QUALITY = 68
MAX_COVERS = PER_ROW * 2  # two rows; anything past this is reported, not hidden

UA = "metehanulusoy-profile-readme/1.0"

QUERY = """
query ($n: String) {
  MediaListCollection(userName: $n, type: ANIME) {
    lists { entries { status progress media {
      episodes duration averageScore
      title { romaji english }
      coverImage { large medium }
    } } } }
}
"""


def fetch() -> list[dict]:
    body = json.dumps({"query": QUERY, "variables": {"n": USER}}).encode()
    req = urllib.request.Request(
        "https://graphql.anilist.co", data=body,
        # AniList answers 403 to urllib's default User-Agent
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"AniList returned errors: {payload['errors']}")
    lists = payload["data"]["MediaListCollection"]["lists"]
    return [entry for group in lists for entry in group["entries"]]


def summarise(entries: list[dict]) -> dict:
    episodes = 0
    minutes = 0
    for e in entries:
        media = e["media"]
        total = media["episodes"] or 0
        watched = total if e["status"] == "COMPLETED" else min(e["progress"] or 0, total or 10**6)
        episodes += watched
        minutes += watched * (media["duration"] or 0)
    return {
        "series": sum(1 for e in entries if e["status"] == "COMPLETED"),
        "episodes": episodes,
        "days": minutes / 1440,
    }


def thumbnail(entry: dict) -> tuple[str, str]:
    """Download one cover and return it as (data-uri, title)."""
    media = entry["media"]
    url = media["coverImage"]["large"] or media["coverImage"]["medium"]
    title = media["title"]["english"] or media["title"]["romaji"] or "?"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        raw = resp.read()
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    image = image.resize((COVER_W, COVER_H), Image.LANCZOS)
    buf = io.BytesIO()
    image.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), title


def render(stats: dict, covers: list[tuple[str, str]]) -> str:
    rows = (len(covers) + PER_ROW - 1) // PER_ROW
    grid_top = 62
    height = grid_top + rows * COVER_H + (rows - 1) * GAP + PAD
    # centre each row so a short last row does not hang off to the left
    tiles = []
    for i, (uri, title) in enumerate(covers):
        row, col = divmod(i, PER_ROW)
        in_row = min(PER_ROW, len(covers) - row * PER_ROW)
        span = in_row * COVER_W + (in_row - 1) * GAP
        x = (WIDTH - span) / 2 + col * (COVER_W + GAP)
        y = grid_top + row * (COVER_H + GAP)
        tiles.append(
            f'<g><title>{html.escape(title)}</title>'
            f'<image x="{x:.1f}" y="{y}" width="{COVER_W}" height="{COVER_H}" '
            f'href="{uri}" clip-path="inset(0 round 4)"/>'
            f'<rect x="{x:.1f}" y="{y}" width="{COVER_W}" height="{COVER_H}" rx="4" '
            f'fill="none" stroke="{PINK}" stroke-opacity=".22"/></g>')

    summary = (f"{stats['series']} series  ·  {stats['episodes']:,} episodes  "
               f"·  {stats['days']:.1f} days")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height:.0f}" role="img"
     aria-label="Anime I have finished on AniList: {html.escape(summary)}">
  <style>
    .t{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
       font-size:20px;font-weight:800;fill:{PINK}}}
    .s{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Ubuntu,Roboto,sans-serif;
       font-size:13px;fill:{INK}}}
    .b{{font-family:"SFMono-Regular",Consolas,Menlo,monospace;font-size:10px;
       letter-spacing:2px;fill:{MUTED}}}
  </style>
  <rect width="{WIDTH}" height="{height:.0f}" rx="6" fill="{BG}"/>
  <text class="t" x="{PAD}" y="38">My Anime List</text>
  <text class="s" x="{PAD + 172}" y="37">{summary}</text>
  <text class="b" x="{WIDTH - PAD}" y="37" text-anchor="end">ANILIST</text>
  {''.join(tiles)}
</svg>
'''


def main() -> None:
    entries = fetch()
    stats = summarise(entries)
    # best-rated first, so the wall opens with the recognisable ones
    ranked = sorted(entries, key=lambda e: -(e["media"]["averageScore"] or 0))
    shown = ranked[:MAX_COVERS]
    if len(ranked) > MAX_COVERS:
        print(f"note: {len(ranked) - MAX_COVERS} entries past the {MAX_COVERS}-cover "
              f"wall are not drawn (lowest rated)")

    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        covers = list(pool.map(thumbnail, shown))

    OUT.write_text(render(stats, covers), encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT.name}: {len(covers)} covers, {stats['series']} series, "
          f"{stats['episodes']} episodes, {stats['days']:.1f} days — {size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
