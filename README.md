<!--
  PROFILE / SOURCE

  What this file deliberately does NOT carry: repository cards and a contribution
  calendar. GitHub already renders both directly beneath this README — pinned repos
  and the real calendar — so duplicating them just made the page twice as long.
  This file is for what GitHub does not show.

  The nameplate and the intro line are hand-written SVGs in assets/, rendered straight
  from this repo; the nameplate honours prefers-reduced-motion. The terminal card and
  the contribution game are built by GitHub Actions in .github/workflows and published
  to this repository's `output` branch. The badges, the wave footer and the Spotify bar
  come from third-party hosts.

  No section headings and no dividers on purpose — the panels carry the structure.

  The Spotify bar uses the spotify-embed theme: it is the only one that shows cover,
  track, artist, a now-playing badge and progress, and the only horizontal one with no
  prefers-color-scheme rules. natemoo-re and novatorem hide their light text behind a
  dark-mode media query, so they wash out for a visitor whose OS is in light mode.
  Never give that image a height — the SVG ships no viewBox, so forcing a size
  stretches the canvas without scaling the content and the text collides.
-->

<picture>
  <source media="(max-width: 600px)" srcset="assets/arcade/nameplate-mobile-v1.svg">
  <img src="assets/arcade/nameplate-v1.svg" width="100%" alt="Metehan Ulusoy — building things, breaking things, learning in public">
</picture>

<p align="center"><sub>PRESS START&nbsp; ·&nbsp; PICK A PROBLEM&nbsp; ·&nbsp; BUILD THE NEXT VERSION</sub></p>

<p align="center">
  <img width="700" src="assets/arcade/intro-v1.svg" alt="Computer Engineering student. I own the whole loop: idea, design, build, ship">
</p>

<p align="center">
  <a href="https://open.spotify.com/user/hnvlh6g6uks1v2ipijfcfsbb9"><img width="460" src="https://spotify-github-profile.kittinanx.com/api/view?uid=hnvlh6g6uks1v2ipijfcfsbb9&cover_image=true&theme=spotify-embed&show_offline=false&interchange=false" alt="What I am listening to on Spotify right now"></a>
</p>

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

<p align="center"><a href="https://github.com/metehanulusoy?tab=repositories"><strong>All repositories →</strong></a></p>

<img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/terminal-hacker.svg" width="100%" alt="Terminal session typing whoami and neofetch, printing live GitHub stats">

<sub>Rebuilt daily from GitHub’s API by a workflow in this repository and published to the <code>output</code> branch.</sub>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph.svg">
  <img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/bomberman-contribution-graph-dark.svg" width="100%" alt="Bomberman clearing a year of GitHub contributions square by square">
</picture>

<!-- spacer: a bare <br> between blocks collapses to ~2px here; an empty centred
     paragraph reliably adds ~40px, which balances this row between the grid above
     and the wave below -->
<p align="center">&nbsp;</p>

<p align="center">
  <a href="https://metehanulusoy.github.io"><strong>PORTFOLIO ↗</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/metehan-ulusoy-1806b6223"><strong>LINKEDIN ↗</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="mailto:ulusoy.metehan03@gmail.com"><strong>EMAIL ↗</strong></a>
</p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=140&section=footer&text=let%27s%20build%20something&fontColor=ffffff&fontSize=28&animation=fadeIn" width="100%" alt="Animated wave footer reading: let's build something">
