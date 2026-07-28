<p align="center">
  <img src="https://raw.githubusercontent.com/reworkd/AgentGPT/main/next/public/banner.png" height="300" alt="AgentGPT Logo"/>
</p>
<p align="center">
  <em>🤖 Assemble, configure, and deploy autonomous AI Agent(s) in your browser. 🤖   </em>
</p>
<p align="center">
    <img alt="Node version" src="https://img.shields.io/static/v1?label=node&message=%20%3E=20&logo=node.js&color=2334D058" />
    <img alt="Python version" src="https://img.shields.io/static/v1?label=python&message=%20%3E=3.12&logo=python&color=2334D058" />
  <a href="https://github.com/js0935/AgentGPT/blob/main/README.md"><img src="https://img.shields.io/badge/lang-English-blue.svg" alt="English"></a>
  <a href="https://github.com/js0935/AgentGPT/blob/main/README.zh.md"><img src="https://img.shields.io/badge/lang-繁體中文-red.svg" alt="繁體中文"></a>
</p>

AgentGPT allows you to configure and deploy Autonomous AI agents.
Name your own custom AI and have it embark on any goal imaginable.
It will attempt to reach the goal by thinking of tasks to do, executing them, and learning from the results 🚀.

> This is a modernized fork of [reworkd/AgentGPT](https://github.com/reworkd/AgentGPT). The upstream project was archived in January 2026. See [differences from upstream](#-differences-from-upstream).

---

## 👨‍🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/en/download) >= 20
- [Python](https://www.python.org/downloads/) >= 3.12
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- An [OpenAI API key](https://platform.openai.com/signup)

### Docker Compose (recommended)

```bash
git clone https://github.com/js0935/AgentGPT.git
cd AgentGPT
cp .env.example .env
# Edit .env to add your API keys
docker compose up
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

### Manual Setup

**Backend**

```bash
cd platform
pip install poetry==1.8.5
poetry install
poetry run python -m reworkd_platform
```

**Frontend**

```bash
cd next
npm install
cp ../.env.example .env
# Edit .env to add your API keys
npx prisma generate
npm run dev
```

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | Next.js 14 (App Router) + FastAPI |
| **Language** | TypeScript 5.7 + Python 3.12 |
| **Database** | MySQL 8.0 + Prisma 5 (frontend) / SQLAlchemy 2.0 (backend) |
| **Auth** | NextAuth.js 4 |
| **Styling** | TailwindCSS 3.4 + HeadlessUI 2 |
| **LLM** | LangChain 0.3 + OpenAI SDK v1 |
| **API** | tRPC 10 (frontend) + REST (backend) |
| **Validation** | Zod 3 + Pydantic v2 |
| **State** | Zustand 4 + TanStack Query 5 |
| **Container** | Docker + Docker Compose |

---

## 🔄 Differences from Upstream

Forked from [reworkd/AgentGPT](https://github.com/reworkd/AgentGPT) (archived Jan 2026). Key upgrades:

- ✅ **Python 3.12**: Pydantic v2, OpenAI SDK v1, LangChain 0.3 (LCEL)
- ✅ **Next.js 14 + App Router**: Pages Router migrated to App Router
- ✅ **Custom i18n**: Migrated from next-i18next to native i18next + react-i18next
- ✅ **Retry logic**: Exponential backoff for OpenAI API calls
- ✅ **Modern Docker**: Multi-stage builds, Node 20, Python 3.12, Poetry 1.8.5
- ✅ **GPT-4o support**: Full support for latest OpenAI models
- ✅ **Leaner dependencies**: Removed 10+ unused packages (kafka, stripe, grpcio, etc.)
- ✅ **CI/CD**: Updated GitHub Actions to Node 20 / Python 3.12
- ✅ **Cleanup**: Removed legacy Pages Router files, unused locale directories, stale docs

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/js0935">js0935</a></sub>
</p>
