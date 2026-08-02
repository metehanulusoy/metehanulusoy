#!/usr/bin/env python3
"""Build the live DEV ARCADE player HUD for the profile README.

Fetches GitHub stats via the GraphQL API and renders
assets/generated/player-hud-v1.svg (desktop) and player-hud-mobile-v1.svg.

Auth:  env GITHUB_TOKEN, falling back to `gh auth token`.
User:  env USER_NAME (default: metehanulusoy).

By default, API failures fall back to assets/generated/stats-cache.json.
With --require-live, an API failure exits before rendering; CI uses this mode
so the output branch keeps its last valid snapshot.

Python 3.12+, standard library only (requests is used when available).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    import requests
except ImportError:  # pragma: no cover - optional fast path
    requests = None
    import urllib.error
    import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED = REPO_ROOT / "assets" / "generated"
CACHE_PATH = GENERATED / "stats-cache.json"
SVG_PATH = GENERATED / "player-hud-v1.svg"
MOBILE_SVG_PATH = GENERATED / "player-hud-mobile-v1.svg"
API_URL = "https://api.github.com/graphql"

DEFAULT_USER = "metehanulusoy"

# ---------------------------------------------------------------- palette ---
MINT = "#36F1CD"
MINT_LIGHT = "#64E8C1"
VIOLET = "#8B5CF6"
BLUE = "#60A5FA"
MAGENTA = "#FF4ECD"
YELLOW = "#FFD166"
CORAL = "#FF6B6B"
PANEL = "#0B1119"
BORDER = "#33404C"
TEXT = "#EAF2F8"
MUTED = "#82909C"
L_PANEL = "#F6F8FA"
L_BORDER = "#D0D7DE"
L_TEXT = "#1F2328"
L_MUTED = "#57606A"

MONO = '"SFMono-Regular", "Cascadia Code", Consolas, "Liberation Mono", Menlo, monospace'

LANG_SHORT = {
    "Jupyter Notebook": "Jupyter",
    "Objective-C": "ObjC",
    "TypeScript": "TypeScript",
}

FALLBACK_STATS = {
    "user": DEFAULT_USER,
    "year": dt.datetime.now(dt.timezone.utc).year,
    "created_year": 2025,
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
        "User-Agent": "dev-arcade-player-hud",
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
def _metric_groups(s: dict, mobile: bool = False) -> str:
    metrics = [
        ("PUBLIC QUESTS", f"{s['repos']:,}", MINT),
        ("TOTAL XP", f"{s['contrib_all_time']:,}", BLUE),
        (f"COMMITS / {s['year']}", f"{s['commits_year']:,}", MAGENTA),
        ("PLAYER SINCE", str(s["created_year"]), YELLOW),
    ]
    groups: list[str] = []
    for index, (label, value, color) in enumerate(metrics):
        if mobile:
            x = 30 + (index % 2) * 332
            y = 178 + (index // 2) * 116
            width, height = 316, 98
            lx, ly, vy, ix = 18, 28, 70, 292
        else:
            x = 390 + (index % 2) * 294
            y = 58 + (index // 2) * 84
            width, height = 278, 78
            lx, ly, vy, ix = 16, 24, 59, 254
        groups.append(
            f'<g transform="translate({x} {y})"><g class="metric m{index}">'
            f'<rect class="tile" width="{width}" height="{height}" rx="10" style="--accent:{color}"/>'
            f'<text class="label" x="{lx}" y="{ly}">{escape(label)}</text>'
            f'<text class="value" x="{lx}" y="{vy}" fill="{color}">{escape(value)}</text>'
            f'<text class="index" x="{ix}" y="{ly}" text-anchor="end" fill="{color}">0{index + 1}</text>'
            '</g></g>'
        )
    return "".join(groups)


def _language_inventory(s: dict, start_x: int, y: int, mobile: bool = False) -> str:
    output: list[str] = []
    x = start_x
    for index, language in enumerate(s.get("langs") or ["Python"]):
        width = max(76 if mobile else 68, (29 if mobile else 24) + len(language) * (8 if mobile else 7))
        output.append(
            f'<g transform="translate({x} {y})"><rect class="pill p{index}" width="{width}" height="{32 if mobile else 26}" rx="{16 if mobile else 13}"/>'
            f'<text class="pill-text" x="{width / 2:.1f}" y="{21 if mobile else 18}" text-anchor="middle">{escape(language)}</text></g>'
        )
        x += width + (10 if mobile else 8)
    return "".join(output)


def render_svg(s: dict) -> str:
    fetched = str(s.get("fetched_at", ""))[:10] or "cached"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Live GitHub player HUD for {escape(s['user'])}: {s['repos']} public quests and {s['contrib_all_time']} total contributions">
  <title>DEV ARCADE — live GitHub player HUD</title>
  <desc>Live public repository, contribution and commit totals generated daily from GitHub.</desc>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#070A11"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{MINT}"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
    <linearGradient id="xp" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{MINT}"/><stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
    <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{BLUE}" stroke-opacity=".045"/></pattern>
  </defs>
  <style>
    text{{font-family:{MONO}}}.panel{{fill:url(#panel)}}.grid{{fill:url(#grid)}}.border{{fill:none;stroke:url(#edge);stroke-width:1.3}}
    .header{{font-size:9px;font-weight:750;letter-spacing:1.4px;fill:#82909C}}.name{{font-size:17px;font-weight:850;fill:{TEXT}}}.class{{font-size:9px;font-weight:750;letter-spacing:1px;fill:{MINT}}}
    .tile{{fill:#0C1420;stroke:var(--accent);stroke-opacity:.35}}.label{{font-size:8px;font-weight:750;letter-spacing:1px;fill:#82909C}}.value{{font-size:24px;font-weight:850}}.index{{font-size:8px;font-weight:800}}
    .pill{{fill:{MINT};fill-opacity:.07;stroke:{MINT};stroke-opacity:.32}}.p1{{stroke:{BLUE}}}.p2{{stroke:{MAGENTA}}}.p3{{stroke:{YELLOW}}}.pill-text{{font-size:9px;font-weight:700;fill:#C8D3DD}}
    .avatar-body{{fill:{BLUE};stroke:#080B12;stroke-width:3}}.avatar-head{{fill:{YELLOW};stroke:#080B12;stroke-width:3}}.limb{{fill:none;stroke:{MINT};stroke-width:6}}.arm{{fill:none;stroke:{MAGENTA};stroke-width:5}}.avatar{{animation:bob 2.4s ease-in-out infinite}}.spark{{animation:spark 1.8s steps(2,end) infinite}}.live{{fill:{MINT};animation:pulse 2.2s ease-in-out infinite}}
    .xp-bg{{fill:#14202B}}.xp{{fill:url(#xp);animation:xp 6s ease-in-out infinite}}.flow{{fill:none;stroke:url(#edge);stroke-dasharray:5 7;animation:flow 3s linear infinite}}.metric{{animation:reveal 16s ease-out infinite}}.m1{{animation-delay:.12s}}.m2{{animation-delay:.24s}}.m3{{animation-delay:.36s}}
    @keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}@keyframes spark{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes xp{{0%{{width:90px}}60%,100%{{width:310px}}}}@keyframes flow{{to{{stroke-dashoffset:-36}}}}@keyframes reveal{{0%{{opacity:.2;transform:translateY(4px)}}5%,100%{{opacity:1;transform:none}}}}
    @media(prefers-color-scheme:light){{.panel{{fill:{L_PANEL}}}.name{{fill:{L_TEXT}}}.header,.label{{fill:{L_MUTED}}}.tile{{fill:#FFFFFF}}.pill-text{{fill:#344252}}.grid{{opacity:.55}}}}
    @media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  </style>
  <rect class="panel" x="1" y="1" width="998" height="258" rx="16"/><rect class="grid" x="1" y="1" width="998" height="258" rx="16"/><rect class="border" x="1" y="1" width="998" height="258" rx="16"/>
  <text class="header" x="26" y="30">PLAYER_HUD.JSON / LIVE GITHUB</text><circle class="live" cx="260" cy="26" r="3"/><text class="header" x="974" y="30" text-anchor="end">AUTO-SAVE / {escape(fetched)} UTC</text><path d="M26 45H974" stroke="#334155"/>
  <g transform="translate(91 112)"><g class="avatar"><rect class="avatar-head" x="-18" y="-57" width="36" height="29" rx="5"/><rect x="-10" y="-48" width="5" height="5"/><rect x="5" y="-48" width="5" height="5"/><path d="M-9-37H9" stroke="#080B12" stroke-width="3"/><rect class="avatar-body" x="-23" y="-25" width="46" height="40" rx="4"/><path class="limb" d="M-12 15v24h-12M12 15v24h12"/><path class="arm" d="M-23-16h-15v22M23-16h15v22"/><g class="spark"><rect x="31" y="-53" width="5" height="16" fill="{MINT}"/><rect x="25" y="-47" width="17" height="5" fill="{MINT}"/></g></g></g>
  <text class="name" x="153" y="89">{escape(s['user'])}@github</text><text class="class" x="153" y="111">CLASS / GENERALIST BUILDER</text><text class="header" x="153" y="136">CURRENT QUEST</text><text class="class" x="153" y="157">LEARN → BUILD → BREAK → SHIP</text>
  <text class="header" x="26" y="203">INVENTORY / TOP LANGUAGES</text>{_language_inventory(s, 26, 216)}
  <path class="flow" d="M365 58V226"/>{_metric_groups(s)}
  <rect class="xp-bg" x="390" y="238" width="584" height="8" rx="4"/><rect class="xp" x="390" y="238" width="560" height="8" rx="4"/><text class="header" x="390" y="229">XP / CURIOSITY + CONSISTENCY</text><text class="header" x="974" y="229" text-anchor="end">{s['age_days']:,} DAYS ONLINE</text>
</svg>"""


def render_mobile_svg(s: dict) -> str:
    fetched = str(s.get("fetched_at", ""))[:10] or "cached"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 520" role="img" aria-label="Live GitHub player HUD for {escape(s['user'])}">
  <title>DEV ARCADE — mobile player HUD</title><desc>Live GitHub totals and top language inventory.</desc>
  <defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#070A11"/></linearGradient><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{MINT}"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient><linearGradient id="xp" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{MINT}"/><stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{BLUE}" stroke-opacity=".045"/></pattern></defs>
  <style>text{{font-family:{MONO}}}.panel{{fill:url(#panel)}}.grid{{fill:url(#grid)}}.border{{fill:none;stroke:url(#edge);stroke-width:1.5}}.header{{font-size:15px;font-weight:750;letter-spacing:1px;fill:#82909C}}.name{{font-size:28px;font-weight:850;fill:{TEXT}}}.class{{font-size:16px;font-weight:750;letter-spacing:.8px;fill:{MINT}}}.tile{{fill:#0C1420;stroke:var(--accent);stroke-opacity:.38}}.label{{font-size:15px;font-weight:750;letter-spacing:.7px;fill:#82909C}}.value{{font-size:34px;font-weight:850}}.index{{font-size:14px;font-weight:800}}.pill{{fill:{MINT};fill-opacity:.07;stroke:{MINT};stroke-opacity:.32}}.p1{{stroke:{BLUE}}}.p2{{stroke:{MAGENTA}}}.p3{{stroke:{YELLOW}}}.pill-text{{font-size:14px;font-weight:700;fill:#C8D3DD}}.avatar-body{{fill:{BLUE};stroke:#080B12;stroke-width:3}}.avatar-head{{fill:{YELLOW};stroke:#080B12;stroke-width:3}}.limb{{fill:none;stroke:{MINT};stroke-width:6}}.arm{{fill:none;stroke:{MAGENTA};stroke-width:5}}.avatar{{animation:bob 2.4s ease-in-out infinite}}.live{{fill:{MINT};animation:pulse 2.2s ease-in-out infinite}}.xp-bg{{fill:#14202B}}.xp{{fill:url(#xp);animation:xp 6s ease-in-out infinite}}@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes xp{{0%{{width:90px}}60%,100%{{width:630px}}}}@media(prefers-color-scheme:light){{.panel{{fill:{L_PANEL}}}.name{{fill:{L_TEXT}}}.header,.label{{fill:{L_MUTED}}}.tile{{fill:#FFFFFF}}.pill-text{{fill:#344252}}.grid{{opacity:.55}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
  <rect class="panel" x="1" y="1" width="718" height="518" rx="20"/><rect class="grid" x="1" y="1" width="718" height="518" rx="20"/><rect class="border" x="1" y="1" width="718" height="518" rx="20"/>
  <text class="header" x="30" y="38">PLAYER_HUD.JSON / LIVE</text><circle class="live" cx="258" cy="34" r="4"/><text class="header" x="690" y="38" text-anchor="end">{escape(fetched)}</text><path d="M30 57H690" stroke="#334155"/>
  <g transform="translate(78 116)"><g class="avatar"><rect class="avatar-head" x="-17" y="-45" width="34" height="27" rx="5"/><rect x="-9" y="-36" width="5" height="5"/><rect x="4" y="-36" width="5" height="5"/><rect class="avatar-body" x="-22" y="-16" width="44" height="36" rx="4"/><path class="limb" d="M-11 20v19h-11M11 20v19h11"/><path class="arm" d="M-22-8h-13v20M22-8h13v20"/></g></g><text class="name" x="135" y="102">{escape(s['user'])}@github</text><text class="class" x="135" y="127">GENERALIST BUILDER / ONLINE</text><text class="header" x="135" y="151">LEARN → BUILD → BREAK → SHIP</text>
  {_metric_groups(s, True)}
  <text class="header" x="30" y="430">INVENTORY / TOP LANGUAGES</text>{_language_inventory(s, 30, 446, True)}
  <rect class="xp-bg" x="30" y="495" width="660" height="9" rx="4.5"/><rect class="xp" x="30" y="495" width="630" height="9" rx="4.5"/>
</svg>"""


# ------------------------------------------------------------------- main ---
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-live",
        action="store_true",
        help="fail instead of rendering cached data when GitHub cannot be reached",
    )
    args = parser.parse_args()

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

    if stats is None and args.require_live:
        print("[error] fresh GitHub telemetry required; leaving published snapshot unchanged")
        return 2

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

    rendered = {
        SVG_PATH: render_svg(stats),
        MOBILE_SVG_PATH: render_mobile_svg(stats),
    }
    for path, svg in rendered.items():
        path.write_text(svg, encoding="utf-8")
        size = path.stat().st_size
        print(f"[ok] wrote {path} ({size} bytes)")
        if size >= 120_000:
            print(f"[error] {path.name} exceeds 120KB budget")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
