<!--
  Synthwave Sunset — Perspektif ızgara üstünde doğan güneş · her blok arası dalga, terminal yok

  Palette: bg #1a0b2e · ink #f7e8ff · accents #FF6B9D #FEC868 #C56CF0 #FF9E64

  No repository cards, contribution calendar, activity feed or contact row:
  GitHub renders every one of those outside this README already.
  The now-playing card uses theme=spotify-embed with mode=dark. `mode` is not in the
  service's documented parameter list but view.py reads it, and the embed template is
  the only one that branches on it — every other theme takes background_color instead,
  which this template hardcodes to white. It is the one way to get this shape without
  a white panel. bar_color does not reach the embed's progress bar; that stays Spotify
  green.

  The views counter is laobi rather than komarev: GitHub's camo proxy gets a hard 503
  from komarev.com on every request, so that badge only ever rendered as a broken
  image. laobi wants its colours URL-encoded with %23 — handed a bare hex it emits
  fill="1a0b2e", which is not a valid colour, and the badge silently falls back to black.

  The raster budget in validate_assets.py is deliberately kept even though no
  raster asset ships right now: the city GIF that prompted it is gone, but the
  ceiling is what stops the next unoptimised drop-in.

  The AniList panel is drawn by scripts/build_anilist_card.py rather than pulled
  from img.anili.st. That service reads User.statistics, and on this account the
  aggregate is stuck at zero — 25 completed entries with progress on 24 of them,
  and count/episodesWatched/minutesWatched have all reported 0 for over eight
  hours. MediaListCollection returns the real rows, so the panel counts those.

  The covers are embedded as base64 JPEGs, not linked: an SVG inside the <img>
  GitHub renders it in is its own document and browsers block its outbound
  requests, so s4.anilist.co URLs would draw an empty grid. Thumbnail size and
  JPEG quality are set to keep the file under the 120 KB ceiling.

  Every animation rests in a readable state under prefers-reduced-motion and
  none uses <script>, which never runs inside the <img> GitHub renders these in.
-->

<img src="assets/header.svg" width="100%" alt="METEHAN ULUSOY">

<p align="center">
  <img src="assets/intro.svg" width="640" alt="">
</p>

<img src="assets/sep1.svg" width="100%" alt="">

<p align="center"><a href="https://open.spotify.com/user/hnvlh6g6uks1v2ipijfcfsbb9"><img width="460" src="https://spotify-github-profile.kittinanx.com/api/view?uid=hnvlh6g6uks1v2ipijfcfsbb9&cover_image=true&show_offline=false&interchange=false&theme=spotify-embed&mode=dark" alt="What I am listening to on Spotify right now"></a></p>

<img src="assets/sep1.svg" width="100%" alt="">

<p align="center">
  <img src="https://img.shields.io/badge/Python-1A0B2E?style=plastic&logo=python&logoColor=3776AB" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-1A0B2E?style=plastic&logo=typescript&logoColor=3178C6" alt="TypeScript">
  <img src="https://img.shields.io/badge/React-1A0B2E?style=plastic&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Next.js-1A0B2E?style=plastic&logo=nextdotjs&logoColor=FFFFFF" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-1A0B2E?style=plastic&logo=fastapi&logoColor=009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-1A0B2E?style=plastic&logo=postgresql&logoColor=4169E1" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-1A0B2E?style=plastic&logo=redis&logoColor=DC382D" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-1A0B2E?style=plastic&logo=docker&logoColor=2496ED" alt="Docker">
</p>

<img src="assets/sep1.svg" width="100%" alt="">

<p align="center">
  <img width="49%" src="https://github-readme-stats-eight-theta.vercel.app/api?username=metehanulusoy&show_icons=true&theme=synthwave&hide_border=true&bg_color=1a0b2e&title_color=FF6B9D&text_color=f7e8ff&icon_color=C56CF0&rank_icon=github" alt="Stars, commits, pull requests and issues">
  <img width="46%" src="https://github-readme-stats-eight-theta.vercel.app/api/top-langs/?username=metehanulusoy&layout=compact&theme=synthwave&hide_border=true&bg_color=1a0b2e&title_color=FF6B9D&text_color=f7e8ff&langs_count=6" alt="Most used languages">
</p>

<p align="center">
  <a href="https://anilist.co/user/metmete"><img width="100%" src="assets/anilist.svg" alt="Anime I have finished, counted from my AniList list"></a>
</p>

<p align="center"><img src="https://visitor-badge.laobi.icu/badge?page_id=metehanulusoy.metehanulusoy&left_text=PROFILE%20VIEWS&left_color=%231a0b2e&right_color=%23FF6B9D" alt="Profile views"></p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a0b2e,100:FF6B9D&height=120&section=footer&text=keep%20shipping&fontColor=ffffff&fontSize=24&animation=fadeIn" width="100%" alt="keep shipping">
