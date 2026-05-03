<h1 align="center">Metehan Ulusoy</h1>

<p align="center">
  <a href="https://github.com/metehanulusoy"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=2600&pause=900&color=A855F7&center=true&vCenter=true&width=720&lines=AI+Engineer+%E2%80%A2+ML+Systems+%E2%80%A2+Banking+Tech;Production+LLM+pipelines%2C+RAG%2C+evals%2C+observability;Computer+Engineering+%40+Recep+Tayyip+Erdogan+University" alt="Typing SVG" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI%20Engineer-Production%20Systems-A855F7?style=for-the-badge&labelColor=1F1F23" />
  <img src="https://img.shields.io/badge/Trabzon%2C%20Turkey-%F0%9F%93%8D-1F1F23?style=for-the-badge&logoColor=white" />
  <a href="https://www.linkedin.com/in/metehan-ulusoy-1806b6223"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=1F1F23" /></a>
  <a href="mailto:ulusoy.metehan03@gmail.com"><img src="https://img.shields.io/badge/Email-Reach%20out-D14836?style=for-the-badge&logo=gmail&logoColor=white&labelColor=1F1F23" /></a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=metehanulusoy&color=A855F7&style=for-the-badge&label=PROFILE+VIEWS" />
  <img src="https://img.shields.io/github/followers/metehanulusoy?style=for-the-badge&color=A855F7&labelColor=1F1F23" />
</p>

---

### About me

- 🎯 Building **production-grade AI systems** — LLM gateways, RAG pipelines, eval harnesses, multi-agent orchestration
- 🏦 Domain focus on **Banking & FinTech** — credit risk, fraud detection, compliance-aware chatbots
- 🧠 **15-project AI Engineering portfolio** in progress: type-safe Python, mypy strict, ≥80 % test coverage on every repo
- 🛠️ Co-authoring most repos with **Claude Opus 4.7** under the Anthropic SDK / Claude Code workflow
- ✉️ Open to AI Engineer roles (remote / EU / Turkey) — `ulusoy.metehan03@gmail.com`

> [!TIP]
> 🚧 **Currently working on:** Project 06 of 15 — *Hybrid-Search RAG Pipeline* (dense + BM25 + RRF fusion + cross-encoder rerank + citation verification). Star the profile to follow new releases.

---

### 🏆 Featured work

<p align="center">
  <a href="https://github.com/metehanulusoy/llm-cost-autopilot">
    <img src="https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=metehanulusoy&repo=llm-cost-autopilot&theme=tokyonight&hide_border=true&title_color=A855F7&icon_color=A855F7&cache_seconds=86400" />
  </a>
  <a href="https://github.com/metehanulusoy/failure-forensics">
    <img src="https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=metehanulusoy&repo=failure-forensics&theme=tokyonight&hide_border=true&title_color=A855F7&icon_color=A855F7&cache_seconds=86400" />
  </a>
</p>
<p align="center">
  <a href="https://github.com/metehanulusoy/llm-arbitration">
    <img src="https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=metehanulusoy&repo=llm-arbitration&theme=tokyonight&hide_border=true&title_color=A855F7&icon_color=A855F7&cache_seconds=86400" />
  </a>
  <a href="https://github.com/metehanulusoy/self-healing-docs">
    <img src="https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=metehanulusoy&repo=self-healing-docs&theme=tokyonight&hide_border=true&title_color=A855F7&icon_color=A855F7&cache_seconds=86400" />
  </a>
</p>

---

### AI Engineering Portfolio &nbsp;<sub>15-project series</sub>

> Each repo: production-shaped Python, FastAPI / Click CLI / GitHub Action, Pydantic v2, mypy strict, ruff lint, ≥ 80 % pytest coverage, Dockerfile, ADRs, MIT license. No real network calls in tests.

| # | Project | What it does | Stack |
|---|---|---|---|
| 01 | [model-regression-detection](https://github.com/metehanulusoy/model-regression-detection) | CI/CD-style regression gate for LLM features. Async eval runner + LLM-as-judge + 7-run drift, PR comment bot, merge-block on critical regressions. | Python · Pydantic · OpenAI · GitHub Actions |
| 02 | [llm-cost-autopilot](https://github.com/metehanulusoy/llm-cost-autopilot) | Multi-provider LLM gateway. sklearn complexity classifier routes each request to the cheapest acceptable model; async LLM-as-judge sampler verifies quality. **>50 % cost reduction vs all-gpt-4o.** | FastAPI · scikit-learn · OpenAI · Anthropic · Ollama |
| 03 | [failure-forensics](https://github.com/metehanulusoy/failure-forensics) | Observability + auto root-cause analysis for multi-step AI pipelines. Decorator-based span tracing, parallel LLM-as-judge backward trace, atomic feedback-to-eval loop, Streamlit explorer. | FastAPI · OpenTelemetry · SQLite WAL · Streamlit |
| 04 | [self-healing-docs](https://github.com/metehanulusoy/self-healing-docs) | GitHub Action that detects when code changes made docs stale, then opens an auto-fix PR or flags affected sections for review. Embedding-based code-to-docs link graph + LLM staleness verifier + style-preservation pass. | GitHub Actions · OpenAI embeddings · PyGithub · unidiff |
| 05 | [llm-arbitration](https://github.com/metehanulusoy/llm-arbitration) | Multi-agent verdict synthesis. Three specialist critics on three different providers grade an output along distinct dimensions; pure disagreement detector + adjudicator agent produce a single confidence-scored verdict. | FastAPI · OpenAI · Anthropic · Ollama · LangGraph-style DAG |

> 06–15 in progress: hybrid-search RAG, semantic caching, text-to-SQL with guardrails, prompt A/B testing, LoRA fine-tuning, LLM gateway with rate limiting, AI feature flags, eval-set generators, multi-modal document processing, and an agent orchestration platform.

---

### Banking &amp; ML Projects

| Project | What it does | Tech |
|---|---|---|
| [credit-risk-scoring](https://github.com/metehanulusoy/credit-risk-scoring) | Credit default prediction with SHAP explainability and banking metrics (KS, Gini, PSI). | XGBoost · scikit-learn · SHAP · FastAPI |
| [fraud-detection-system](https://github.com/metehanulusoy/fraud-detection-system) | Real-time fraud detection — ML ensemble + rule-based alerts. | XGBoost · Isolation Forest · FastAPI |
| [banking-chatbot-rag](https://github.com/metehanulusoy/banking-chatbot-rag) | RAG chatbot for Turkish banking FAQs with guardrails &amp; compliance. | LangChain · ChromaDB · FastAPI |

<details>
<summary><b>📊 Credit risk model — evaluation snapshots</b></summary>

<br/>

![Evaluation Dashboard](https://raw.githubusercontent.com/metehanulusoy/credit-risk-scoring/main/docs/evaluation_dashboard.png)

![SHAP Importance](https://raw.githubusercontent.com/metehanulusoy/credit-risk-scoring/main/docs/shap_importance.png)

</details>

<details>
<summary><b>🧰 Side projects &amp; experiments</b></summary>

<br/>

| Project | Description |
|---|---|
| [pdf-rag-app](https://github.com/metehanulusoy/pdf-rag-app) | AI-powered PDF Q&amp;A system with RAG &amp; OpenAI. |
| [awesome-n8n-workflows](https://github.com/metehanulusoy/awesome-n8n-workflows) | 2 055 production-ready n8n automation templates. |
| [price-tracker-bot](https://github.com/metehanulusoy/price-tracker-bot) | Price tracking bot for Trendyol &amp; Amazon with Telegram alerts. |
| [emotion-detector](https://github.com/metehanulusoy/emotion-detector) | Real-time facial emotion detection using face-api.js. |

</details>

---

### Tech I work with

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,docker,sklearn,postgres,sqlite,redis,git,githubactions,linux&theme=dark" alt="Stack icons" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black" />
  <img src="https://img.shields.io/badge/mypy-2A6DB2?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-337AB7?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=white" />
  <img src="https://img.shields.io/badge/uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" />
</p>

---

### Engineering standards I default to

```diff
+ Type-safe Python (Pydantic v2 + mypy --strict on every repo)
+ ≥80% pytest coverage with httpx.MockTransport — no real network calls in CI
+ Conventional commits, ADRs ("Why" + "Trade-offs" + "Revisit if")
+ Async-first I/O (asyncio + httpx + tenacity exponential backoff)
+ Structured JSON logging (structlog) with stable event names
+ Dockerfile + docker-compose + Makefile + GitHub Actions matrix py3.11/3.12
- No untyped public APIs · No secrets in commits · No flaky tests
```

---

### GitHub stats

<p align="center">
  <img src="https://github-readme-stats-eight-theta.vercel.app/api?username=metehanulusoy&show_icons=true&theme=tokyonight&hide_border=true&title_color=A855F7&icon_color=A855F7&include_all_commits=true&cache_seconds=86400" height="170" />
  <img src="https://github-readme-stats-eight-theta.vercel.app/api/top-langs/?username=metehanulusoy&layout=compact&theme=tokyonight&hide_border=true&title_color=A855F7&langs_count=8&cache_seconds=86400" height="170" />
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=metehanulusoy&theme=tokyonight&hide_border=true&background=1A1B27&ring=A855F7&fire=A855F7&currStreakLabel=A855F7" height="170" />
</p>

#### 🐍 Watch my contributions get eaten

<p align="center">
  <img src="https://raw.githubusercontent.com/metehanulusoy/metehanulusoy/output/snake-dark.svg" alt="snake animation" />
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=metehanulusoy&theme=tokyo-night&hide_border=true&bg_color=1A1B27&color=A855F7&line=A855F7&point=FFFFFF&area=true&area_color=A855F7" />
</p>

---

### 💭 Wisdom of the day

<p align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=tokyonight" alt="Quote" />
</p>

---

### Connect

<p align="center">
  <a href="https://www.linkedin.com/in/metehan-ulusoy-1806b6223"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <a href="https://github.com/metehanulusoy"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
  <a href="mailto:ulusoy.metehan03@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
</p>

<p align="center"><sub>Crafted with care · Most repos co-authored with <b>Claude Opus 4.7</b> via the Anthropic SDK</sub></p>
