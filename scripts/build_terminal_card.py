#!/usr/bin/env python3
"""Build the live GitHub release-ledger SVG for the profile README.

Fetches GitHub stats via the GraphQL API and renders
assets/generated/terminal-card.svg (desktop) and terminal-card-mobile.svg.

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
SVG_PATH = GENERATED / "terminal-card.svg"
MOBILE_SVG_PATH = GENERATED / "terminal-card-mobile.svg"
API_URL = "https://api.github.com/graphql"

DEFAULT_USER = "metehanulusoy"

# ---------------------------------------------------------------- palette ---
MINT = "#36F1CD"
MINT_LIGHT = "#64E8C1"
VIOLET = "#8B5CF6"
BLUE = "#60A5FA"
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
def render_svg(s: dict) -> str:
    year = s["year"]
    metrics = [
        ("PUBLIC REPOS", f"{s['repos']:,}"),
        ("CONTRIBUTIONS", f"{s['contrib_all_time']:,}"),
        (f"COMMITS / {year}", f"{s['commits_year']:,}"),
        ("ACCOUNT SINCE", str(s["created_year"])),
    ]
    metric_groups = []
    for index, (label, value) in enumerate(metrics):
        x = 26 + index * 239
        metric_groups.append(
            f'<g class="metric m{index}" transform="translate({x} 60)">'
            '<rect class="tile" width="226" height="88" rx="12"/>'
            f'<text class="label" x="18" y="27">{escape(label)}</text>'
            f'<text class="value" x="18" y="66">{escape(value)}</text>'
            f'<text class="index" x="204" y="27" text-anchor="end">0{index + 1}</text>'
            '</g>'
        )

    lang_groups = []
    x = 190
    for index, language in enumerate(s.get("langs") or ["Python"]):
        width = max(70, 26 + len(language) * 8)
        lang_groups.append(
            f'<g transform="translate({x} 172)"><rect class="pill" width="{width}" height="27" rx="13.5"/>'
            f'<text class="pill-text" x="{width / 2:.1f}" y="18" text-anchor="middle">{escape(language)}</text></g>'
        )
        x += width + 10

    fetched = str(s.get("fetched_at", ""))[:10] or "cached"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 230" role="img" aria-label="Live GitHub release ledger for {escape(s['user'])}: {s['repos']} public repositories and {s['contrib_all_time']} contributions">
  <title>Release Ledger — live GitHub telemetry</title>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0E151E"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>
    <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="0"><stop stop-color="{MINT}" stop-opacity=".72"/><stop offset=".55" stop-color="{BLUE}" stop-opacity=".5"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".72"/></linearGradient>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{MINT_LIGHT}" stroke-opacity=".035"/></pattern>
    <filter id="glow" x="-300%" y="-300%" width="700%" height="700%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>
  <style>
    text{{font-family:{MONO}}}.panel{{fill:url(#panel);stroke:{BORDER}}}.grid{{fill:url(#grid)}}
    .header{{font-size:10px;font-weight:650;letter-spacing:1.5px;fill:{MUTED}}}.live{{fill:{MINT_LIGHT}}}
    .tile{{fill:{MINT};fill-opacity:.035;stroke:{MINT};stroke-opacity:.13}}.label{{font-size:9px;font-weight:650;letter-spacing:1.15px;fill:{MUTED}}}
    .value{{font-size:26px;font-weight:720;fill:{TEXT}}}.index{{font-size:8px;font-weight:650;fill:{MINT};opacity:.7}}
    .pill{{fill:{MINT};fill-opacity:.07;stroke:{MINT};stroke-opacity:.2}}.pill-text{{font-size:10px;font-weight:650;fill:#BAC5CF}}
    .signal{{fill:none;stroke:url(#edge);stroke-width:1.2;stroke-dasharray:4 10;animation:flow 4s linear infinite}}
    .pulse{{animation:pulse 3s ease-in-out infinite}}.metric{{animation:reveal 30s ease-out infinite}}.m1{{animation-delay:.12s}}.m2{{animation-delay:.24s}}.m3{{animation-delay:.36s}}
    @keyframes flow{{to{{stroke-dashoffset:-56}}}}@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes reveal{{0%{{opacity:0}}4%,100%{{opacity:1}}}}
    @media(prefers-color-scheme:light){{.panel{{fill:{L_PANEL};stroke:{L_BORDER}}}.grid{{opacity:.5}}.header,.label{{fill:{L_MUTED}}}.value{{fill:{L_TEXT}}}.pill-text{{fill:#3F4852}}.tile{{fill:#FFFFFF;stroke-opacity:.22}}}}
    @media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.motion{{display:none}}}}
  </style>
  <rect class="panel" x="1" y="1" width="998" height="228" rx="16"/><rect class="grid" x="1" y="1" width="998" height="228" rx="16"/>
  <text class="header" x="26" y="31">RELEASE LEDGER / LIVE GITHUB SIGNAL</text><circle class="live pulse" cx="275" cy="27.5" r="3"/>
  <text class="header" x="974" y="31" text-anchor="end">SYNC / {escape(fetched)} UTC</text>
  {''.join(metric_groups)}
  <path class="signal" d="M26 211H974"/>
  <text class="header" x="26" y="190">LANGUAGE VECTOR</text>
  {''.join(lang_groups)}
  <text class="header" x="974" y="190" text-anchor="end">{s['age_days']:,} DAYS ON GITHUB</text>
  <g class="motion"><circle r="3" fill="{MINT}" filter="url(#glow)"><animateMotion dur="8s" repeatCount="indefinite" path="M26 211H974"/></circle><circle r="2.5" fill="{VIOLET}"><animateMotion dur="8s" begin="-4s" repeatCount="indefinite" path="M26 211H974"/></circle></g>
</svg>"""


def render_mobile_svg(s: dict) -> str:
    year = s["year"]
    metrics = [
        ("PUBLIC REPOS", f"{s['repos']:,}"),
        ("CONTRIBUTIONS", f"{s['contrib_all_time']:,}"),
        (f"COMMITS / {year}", f"{s['commits_year']:,}"),
        ("ACCOUNT SINCE", str(s["created_year"])),
    ]
    groups = []
    for index, (label, value) in enumerate(metrics):
        x = 28 + (index % 2) * 278
        y = 68 + (index // 2) * 128
        groups.append(
            f'<g transform="translate({x} {y})"><rect class="tile" width="266" height="112" rx="14"/>'
            f'<text class="label" x="18" y="30">{escape(label)}</text><text class="value" x="18" y="76">{escape(value)}</text>'
            f'<text class="index" x="242" y="30" text-anchor="end">0{index + 1}</text></g>'
        )

    languages = " / ".join(s.get("langs") or ["Python"])
    fetched = str(s.get("fetched_at", ""))[:10] or "cached"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 390" role="img" aria-label="Live GitHub release ledger for {escape(s['user'])}">
  <title>Release Ledger — mobile</title>
  <defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0E151E"/><stop offset="1" stop-color="{PANEL}"/></linearGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{MINT_LIGHT}" stroke-opacity=".035"/></pattern></defs>
  <style>text{{font-family:{MONO}}}.panel{{fill:url(#panel);stroke:{BORDER}}}.grid{{fill:url(#grid)}}.header{{font-size:11px;font-weight:650;letter-spacing:1.3px;fill:{MUTED}}}.live{{fill:{MINT_LIGHT};animation:p 3s ease-in-out infinite}}.tile{{fill:{MINT};fill-opacity:.035;stroke:{MINT};stroke-opacity:.17}}.label{{font-size:11px;font-weight:650;letter-spacing:1.1px;fill:{MUTED}}}.value{{font-size:34px;font-weight:720;fill:{TEXT}}}.index{{font-size:10px;font-weight:650;fill:{MINT}}}.lang{{font-size:12px;font-weight:650;letter-spacing:.8px;fill:#BAC5CF}}.line{{stroke:{MINT};stroke-opacity:.35;stroke-dasharray:4 10;animation:f 4s linear infinite}}@keyframes p{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes f{{to{{stroke-dashoffset:-56}}}}@media(prefers-color-scheme:light){{.panel{{fill:{L_PANEL};stroke:{L_BORDER}}}.grid{{opacity:.5}}.header,.label{{fill:{L_MUTED}}}.value{{fill:{L_TEXT}}}.tile{{fill:#FFF;stroke-opacity:.24}}.lang{{fill:#3F4852}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
  <rect class="panel" x="1" y="1" width="598" height="388" rx="18"/><rect class="grid" x="1" y="1" width="598" height="388" rx="18"/>
  <text class="header" x="28" y="36">RELEASE LEDGER / LIVE</text><circle class="live" cx="210" cy="32" r="3.5"/><text class="header" x="572" y="36" text-anchor="end">{escape(fetched)}</text>
  {''.join(groups)}
  <text class="header" x="28" y="342">LANGUAGE VECTOR</text><text class="lang" x="28" y="366">{escape(languages)}</text><path class="line" d="M28 378H572"/>
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
