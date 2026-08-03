<!--
  PROFILE / SOURCE

  Reading order is deliberate: who → what I work with → proof it is live → a human
  note → how to reach me. Each of those is one block, separated by an empty centred
  paragraph. A bare <br> collapses to about 2px between blocks; the empty paragraph
  reliably adds ~40px, which is what keeps the blocks from running together.

  What this file deliberately does NOT carry: repository cards and a contribution
  calendar. GitHub renders both directly beneath this README — the pinned repos and
  the real calendar — so duplicating them only made the page twice as long. This file
  is for what GitHub does not show.

  Everything is centred, including captions. Panels that span the column use
  width="100%"; the two stat cards sit two-up at 49% and 46% so their optical widths
  match. The now-playing chip is the one floated element, pinned to the top corner.

  A streak card sat here and was removed: streak-stats answers with an HTML
  "Application Error" page under a 200 status roughly one request in four, which
  renders as a broken image. Every remaining third-party source was sampled and came
  back clean — shields, capsule-render, the spotify bar and this mirror.

  The nameplate and the intro line are hand-written SVGs in assets/, rendered straight
  from this repo; the nameplate honours prefers-reduced-motion. The terminal card and
  the contribution game are built by GitHub Actions in .github/workflows and published
  to this repository's `output` branch. The badges, the two stat cards, the wave footer
  and the Spotify bar come from third-party hosts.

  github-readme-stats' own instance is 503, so the language card points at a mirror.

  The now-playing chip uses the compact theme without a cover: it is small enough for
  the corner and carries no prefers-color-scheme rules. natemoo-re and novatorem look
  better but hide their light text behind a dark-mode media query, so they wash out for
  a visitor whose OS is in light mode. Never give that image a height or a width above
  its own 320px — the SVG ships no viewBox, so enlarging it stretches the canvas
  without scaling the content and the text collides.

  Everything third-party here was sampled before it went in: the stat cards 5/5, the
  view counter 3/3, shields, capsule-render and the chip clean. A streak card was tried
  and dropped at 2 failures in 8.
-->

<picture>
  <source media="(max-width: 600px)" srcset="assets/nameplate-mobile.svg">
  <img src="assets/nameplate.svg" width="100%" alt="Metehan Ulusoy — building things, breaking things, learning in public">
</picture>

<img src="assets/marquee.svg" width="100%" alt="Build, break, learn, ship — AI and LLM systems, RAG, caching, evaluation, web and product, automation that sticks">

<a href="https://open.spotify.com/user/hnvlh6g6uks1v2ipijfcfsbb9"><img align="right" width="320" src="https://spotify-github-profile.kittinanx.com/api/view?uid=hnvlh6g6uks1v2ipijfcfsbb9&cover_image=false&theme=compact&show_offline=false&background_color=0d1117&interchange=false" alt="What I am listening to on Spotify right now"></a>

<p align="center">
  <img width="620" src="assets/intro.svg" alt="Computer Engineering student. I own the whole loop: idea, design, build, ship">
</p>

<br clear="right">

<p align="center">
  <img src="https://img.shields.io/badge/Python-0D1117?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-0D1117?style=for-the-badge&logo=typescript&logoColor=3178C6" alt="TypeScript">
  <img src="https://img.shields.io/badge/React-0D1117?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Next.js-0D1117?style=for-the-badge&logo=nextdotjs&logoColor=FFFFFF" alt="Next.js">
  <img src="https://img.shields.io/badge/FastAPI-0D1117?style=for-the-badge&logo=fastapi&logoColor=009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-0D1117?style=for-the-badge&logo=postgresql&logoColor=4169E1" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-0D1117?style=for-the-badge&logo=redis&logoColor=DC382D" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-0D1117?style=for-the-badge&logo=docker&logoColor=2496ED" alt="Docker">
</p>

<p align="center">&nbsp;</p>

<p align="center">
  <img width="49%" src="https://github-readme-stats-eight-theta.vercel.app/api?username=metehanulusoy&show_icons=true&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=32F5C4&text_color=c9d1d9&icon_color=FF4ECD&rank_icon=github" alt="Stars, commits, pull requests and issues">
  <img width="46%" src="https://github-readme-stats-eight-theta.vercel.app/api/top-langs/?username=metehanulusoy&layout=compact&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=32F5C4&text_color=c9d1d9&langs_count=6" alt="Most used languages across my repositories">
</p>

<img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/terminal-hacker.svg" width="100%" alt="Terminal session typing whoami and neofetch, printing live GitHub stats">

<p align="center"><sub>Rebuilt daily from GitHub’s API by a workflow in this repository, published to the <code>output</code> branch.</sub></p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph.svg">
  <img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph-dark.svg" width="100%" alt="Bomberman clearing a year of GitHub contributions square by square">
</picture>

<p align="center"><sub>A year of commits, played as a level.</sub></p>

<img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/profile-night-rainbow.svg" width="100%" alt="Isometric 3D calendar of the last year of contributions">

<p align="center">&nbsp;</p>

<p align="center">
  <a href="https://metehanulusoy.github.io"><strong>PORTFOLIO ↗</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/metehan-ulusoy-1806b6223"><strong>LINKEDIN ↗</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="mailto:ulusoy.metehan03@gmail.com"><strong>EMAIL ↗</strong></a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=metehanulusoy&style=for-the-badge&color=0D1117&label=PROFILE+VIEWS" alt="Profile views">
</p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=140&section=footer&text=let%27s%20build%20something&fontColor=ffffff&fontSize=28&animation=fadeIn" width="100%" alt="Animated wave footer reading: let's build something">
