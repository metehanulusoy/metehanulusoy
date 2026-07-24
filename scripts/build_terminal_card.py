#!/usr/bin/env python3
"""Build the live-stats neofetch-style terminal card SVG.

Fetches GitHub stats via the GraphQL API and renders
assets/generated/terminal-card.svg (viewBox 0 0 560 340).

Auth:  env GITHUB_TOKEN, falling back to `gh auth token`.
User:  env USER_NAME (default: metehanulusoy).

On any API failure the script falls back to the cached JSON at
assets/generated/stats-cache.json (written on every successful fetch),
so CI never produces a broken card.

Python 3.12+, stdlib + requests only.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    import requests
except ImportError:  # pragma: no cover - requests is in requirements.txt
    requests = None
    import urllib.error
    import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED = REPO_ROOT / "assets" / "generated"
CACHE_PATH = GENERATED / "stats-cache.json"
SVG_PATH = GENERATED / "terminal-card.svg"
API_URL = "https://api.github.com/graphql"

DEFAULT_USER = "metehanulusoy"

# ---------------------------------------------------------------- palette ---
PURPLE = "#A855F7"
PURPLE_DEEP = "#7C3AED"
PURPLE_LIGHT = "#C084FC"
BLUE = "#7AA2F7"
PANEL = "#161B22"
BORDER = "#30363D"
TEXT = "#C9D1D9"
MUTED = "#8B949E"
GREEN = "#9ECE6A"
L_PANEL = "#F6F8FA"
L_BORDER = "#D0D7DE"
L_TEXT = "#1F2328"
L_MUTED = "#6E7781"
L_GREEN = "#1A7F37"
L_BLUE = "#4863D4"

MONO = '"SFMono-Regular", "Cascadia Code", Consolas, "Liberation Mono", Menlo, monospace'

SWATCHES = [BORDER, PURPLE_DEEP, PURPLE, PURPLE_LIGHT, BLUE, GREEN, TEXT, MUTED]

LANG_SHORT = {
    "Jupyter Notebook": "Jupyter",
    "Objective-C": "ObjC",
    "TypeScript": "TypeScript",
}

FALLBACK_STATS = {
    "user": DEFAULT_USER,
    "year": dt.datetime.now(dt.timezone.utc).year,
    "created_year": 2020,
    "repos": 0,
    "stars": 0,
    "followers": 0,
    "commits_year": 0,
    "contrib_all_time": 0,
    "age_days": 0,
    "langs": ["Python", "TypeScript", "Swift", "Shell"],
}

MAIN_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!, $cursor: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
      contributionYears
    }
    repositories(
      first: 100
      after: $cursor
      privacy: PUBLIC
      ownerAffiliations: OWNER
    ) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        isFork
        stargazerCount
        languages(first: 6, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


# ------------------------------------------------------------------ fetch ---
def get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    try:
        proc = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=15
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except OSError:
        pass
    return ""


def gql(token: str, query: str, variables: dict) -> dict:
    payload = {"query": query, "variables": variables}
    headers = {
        "Authorization": f"bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "profile-terminal-card",
    }
    if requests is not None:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        body = resp.json()
    else:  # stdlib fallback
        req = urllib.request.Request(
            API_URL, data=json.dumps(payload).encode(), headers=headers
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
    if body.get("errors"):
        raise RuntimeError(f"GraphQL errors: {body['errors']}")
    if not body.get("data", {}).get("user"):
        raise RuntimeError(f"No user data returned for query (login unknown?)")
    return body["data"]["user"]


def fetch_all_time_contributions(token: str, login: str, years: list[int]) -> int:
    """Sum contributionCalendar.totalContributions across every account year."""
    parts = []
    for y in years:
        parts.append(
            f'y{y}: contributionsCollection('
            f'from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z")'
            "{ contributionCalendar { totalContributions } }"
        )
    query = (
        "query($login: String!) { user(login: $login) { " + " ".join(parts) + " } }"
    )
    user = gql(token, query, {"login": login})
    return sum(
        user[f"y{y}"]["contributionCalendar"]["totalContributions"] for y in years
    )


def fetch_stats(token: str, login: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    year = now.year
    year_from = f"{year}-01-01T00:00:00Z"
    year_to = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    stars = 0
    lang_sizes: dict[str, int] = {}
    repo_count = 0
    cursor = None
    user = None
    for _ in range(10):  # max 1000 repos
        page = gql(
            token,
            MAIN_QUERY,
            {"login": login, "from": year_from, "to": year_to, "cursor": cursor},
        )
        if user is None:
            user = page
        repos = page["repositories"]
        repo_count = repos["totalCount"]
        for node in repos["nodes"]:
            stars += node["stargazerCount"]
            if node["isFork"]:
                continue  # languages: own work only
            for edge in node["languages"]["edges"]:
                name = edge["node"]["name"]
                lang_sizes[name] = lang_sizes.get(name, 0) + edge["size"]
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]

    coll = user["contributionsCollection"]
    commits_year = coll["totalCommitContributions"]
    years = coll.get("contributionYears") or [year]
    try:
        contrib_all_time = fetch_all_time_contributions(token, login, sorted(years))
    except Exception as exc:  # graceful fallback per spec
        print(f"[warn] per-year contributions failed ({exc}); using fallback sum")
        contrib_all_time = (
            coll["contributionCalendar"]["totalContributions"]
            + coll["restrictedContributionsCount"]
        )

    created = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    top_langs = [
        LANG_SHORT.get(name, name)
        for name, _ in sorted(lang_sizes.items(), key=lambda kv: -kv[1])[:4]
    ]

    return {
        "user": login,
        "fetched_at": year_to,
        "year": year,
        "created_year": created.year,
        "repos": repo_count,
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits_year": commits_year,
        "contrib_all_time": contrib_all_time,
        "age_days": (now - created).days,
        "langs": top_langs or ["Python"],
    }


# ----------------------------------------------------------------- render ---
ASCII_MU = [
    "███╗   ███╗ ██╗   ██╗",
    "████╗ ████║ ██║   ██║",
    "██╔████╔██║ ██║   ██║",
    "██║╚██╔╝██║ ██║   ██║",
    "██║ ╚═╝ ██║ ╚██████╔╝",
    "╚═╝     ╚═╝  ╚═════╝ ",
]

CHAR_W = 7.5  # mono char width at font-size 12.5 (0.6em)
RIGHT_X = 200
RIGHT_BUDGET = 45  # chars that fit between x=200 and the panel edge


def fit_langs(langs: list[str], label: str) -> str:
    """Join top languages, dropping from the end until the row fits."""
    langs = list(langs)
    while langs:
        value = " · ".join(langs)
        if len(label) + 1 + len(value) <= RIGHT_BUDGET:
            return value
        langs.pop()
    return "—"


def render_svg(s: dict) -> str:
    year = s["year"]
    langs_label = "Langs:"
    rows = [
        ("OS:", "macOS · zsh · tokyonight"),
        ("Role:", "AI Engineer"),
        ("Repos:", f"{s['repos']} public"),
        ("Stars:", f"★ {s['stars']:,}"),
        ("Followers:", f"{s['followers']:,}"),
        (f"Commits({year}):", f"{s['commits_year']:,}"),
        ("Age:", f"{s['age_days']:,} days on GitHub"),
        (langs_label, fit_langs(s["langs"], langs_label)),
    ]

    # Reveal order: 6 logo lines, caption, location, user@host, separator,
    # 8 stat rows, swatches, prompt  -> 20 staggered steps over ~4s of a 60s loop.
    n_seq = 6 + 2 + 2 + len(rows) + 2
    key_css = []
    for i in range(n_seq):
        t0 = 0.35 + i * 0.19
        a = t0 / 60 * 100
        b = (t0 + 0.30) / 60 * 100
        key_css.append(
            f"@keyframes s{i}{{0%,{a:.2f}%{{opacity:0}}{b:.2f}%,100%{{opacity:1}}}}"
            f".q{i}{{animation:s{i} 60s linear infinite}}"
        )

    style = f"""
  text{{font-family:{MONO};}}
  .panel{{fill:{PANEL};stroke:{BORDER};}}
  .lab{{fill:{PURPLE};font-weight:600;}}
  .val{{fill:{TEXT};}}
  .muted{{fill:{MUTED};}}
  .host{{fill:{BLUE};}}
  .logo{{fill:{PURPLE};}}
  .prompt{{fill:{GREEN};}}
  .cursor{{fill:{TEXT};}}
  .swb{{stroke:{BORDER};stroke-width:0.5;}}
  .dashline{{stroke:{PURPLE_DEEP};stroke-width:1;stroke-dasharray:5 6;opacity:0.55;
    animation:dashflow 3s linear infinite;}}
  @keyframes dashflow{{to{{stroke-dashoffset:-22;}}}}
  .blink{{animation:blink 1.1s linear infinite;}}
  @keyframes blink{{0%,54%{{opacity:1}}55%,100%{{opacity:0}}}}
  {"".join(key_css)}
  @media (prefers-color-scheme: light){{
    .panel{{fill:{L_PANEL};stroke:{L_BORDER};}}
    .lab{{fill:{PURPLE_DEEP};}}
    .val{{fill:{L_TEXT};}}
    .muted{{fill:{L_MUTED};}}
    .host{{fill:{L_BLUE};}}
    .logo{{fill:{PURPLE_DEEP};}}
    .prompt{{fill:{L_GREEN};}}
    .cursor{{fill:{L_TEXT};}}
    .swb{{stroke:{L_BORDER};}}
  }}
  @media (prefers-reduced-motion: reduce){{ * {{ animation: none !important; }} }}
"""

    parts: list[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 340" role="img" '
        f'aria-label="Neofetch-style terminal card with live GitHub stats for {escape(s["user"])}">'
    )
    parts.append(f"<style>{style}</style>")
    # panel + title bar
    parts.append('<rect class="panel" x="4" y="4" width="552" height="332" rx="12"/>')
    parts.append(
        '<circle cx="26" cy="27" r="5" fill="#FF5F57"/>'
        '<circle cx="44" cy="27" r="5" fill="#FEBC2E"/>'
        '<circle cx="62" cy="27" r="5" fill="#28C840"/>'
    )
    parts.append(
        '<text class="muted" x="280" y="31" font-size="12" text-anchor="middle">'
        "metehan@github: ~</text>"
    )
    # dash-flow separator under the header
    parts.append('<path class="dashline" d="M20 46 H540" fill="none"/>')

    seq = 0
    # left column: ASCII MU logogram
    y = 140
    for line in ASCII_MU:
        parts.append(
            f'<text class="logo q{seq}" x="26" y="{y}" font-size="11" '
            f'xml:space="preserve">{escape(line)}</text>'
        )
        seq += 1
        y += 12
    parts.append(
        f'<text class="muted q{seq}" x="26" y="226" font-size="10">'
        "// ai · engineer</text>"
    )
    seq += 1
    parts.append(
        f'<text class="muted q{seq}" x="26" y="244" font-size="10">'
        "Trabzon, Türkiye</text>"
    )
    seq += 1

    # right column: user@host, separator, stat rows
    parts.append(
        f'<text class="q{seq}" x="{RIGHT_X}" y="78" font-size="13">'
        f'<tspan class="lab">metehan</tspan><tspan class="muted">@</tspan>'
        f'<tspan class="host">github</tspan></text>'
    )
    seq += 1
    parts.append(
        f'<text class="muted q{seq}" x="{RIGHT_X}" y="96" font-size="12.5" '
        f'opacity="0.8">{"─" * 30}</text>'
    )
    seq += 1
    y = 118
    for label, value in rows:
        parts.append(
            f'<text class="q{seq}" x="{RIGHT_X}" y="{y}" font-size="12.5">'
            f'<tspan class="lab">{escape(label)}</tspan>'
            f'<tspan class="val" dx="7">{escape(value)}</tspan></text>'
        )
        seq += 1
        y += 20

    # swatch row: terminal palette featuring purples
    sw = [
        f'<rect class="swb" x="{RIGHT_X + i * 24}" y="272" width="16" height="16" '
        f'rx="3" fill="{c}"/>'
        for i, c in enumerate(SWATCHES)
    ]
    parts.append(f'<g class="q{seq}">{"".join(sw)}</g>')
    seq += 1

    # prompt line + blinking cursor
    echo = f"{s['contrib_all_time']:,} contributions since {s['created_year']}"
    cursor_x = 26 + (2 + len(echo)) * CHAR_W + 6
    parts.append(
        f'<g class="q{seq}">'
        f'<text x="26" y="314" font-size="12.5"><tspan class="prompt">❯</tspan>'
        f'<tspan class="val" dx="7">{escape(echo)}</tspan></text>'
        f'<rect class="cursor blink" x="{cursor_x:.0f}" y="303" width="8" height="14" rx="1"/>'
        "</g>"
    )
    parts.append("</svg>")
    return "".join(parts)


# ------------------------------------------------------------------- main ---
def main() -> int:
    login = os.environ.get("USER_NAME", DEFAULT_USER).strip() or DEFAULT_USER
    GENERATED.mkdir(parents=True, exist_ok=True)

    stats = None
    token = get_token()
    if not token:
        print("[warn] no GITHUB_TOKEN and `gh auth token` unavailable")
    else:
        try:
            stats = fetch_stats(token, login)
            CACHE_PATH.write_text(
                json.dumps(stats, indent=2) + "\n", encoding="utf-8"
            )
            print(f"[ok] fetched live stats for {login}; cache updated")
        except Exception as exc:
            print(f"[warn] GitHub API fetch failed: {exc}")

    if stats is None:
        if CACHE_PATH.exists():
            try:
                stats = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
                print(f"[ok] using cached stats from {CACHE_PATH.name}")
            except (OSError, json.JSONDecodeError) as exc:
                print(f"[warn] cache unreadable: {exc}")
        if stats is None:
            print("[warn] no cache either; rendering placeholder values")
            stats = dict(FALLBACK_STATS)

    svg = render_svg(stats)
    SVG_PATH.write_text(svg, encoding="utf-8")
    size = SVG_PATH.stat().st_size
    print(f"[ok] wrote {SVG_PATH} ({size} bytes)")
    if size >= 120_000:
        print("[error] SVG exceeds 120KB budget")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
