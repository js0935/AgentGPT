<p align="center">
  <img src="https://raw.githubusercontent.com/reworkd/AgentGPT/main/next/public/banner.png" height="300" alt="AgentGPT Logo"/>
</p>
<p align="center">
  <em>🤖 在瀏覽器中組裝、設定並部署自主 AI 代理人。🤖</em>
</p>
<p align="center">
  <img alt="Node version" src="https://img.shields.io/static/v1?label=node&message=%20%3E=20&logo=node.js&color=2334D058" />
  <img alt="Python version" src="https://img.shields.io/static/v1?label=python&message=%20%3E=3.12&logo=python&color=2334D058" />
  <a href="https://github.com/js0935/AgentGPT/blob/main/README.md"><img src="https://img.shields.io/badge/lang-English-blue.svg" alt="English"></a>
  <a href="https://github.com/js0935/AgentGPT/blob/main/README.zh.md"><img src="https://img.shields.io/badge/lang-繁體中文-red.svg" alt="繁體中文"></a>
</p>

AgentGPT 讓您能夠設定並部署自主 AI 代理人。為您的自訂 AI 命名，讓它朝著任何可以想像的目標前進 🚀。

---

## ✨ 功能展示

最佳體驗方式：Fork 本專案並自行部署。

---

## 🚀 快速開始

### 前置需求

- [Node.js](https://nodejs.org/en/download) >= 20
- [Python](https://www.python.org/downloads/) >= 3.12
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [OpenAI API 金鑰](https://platform.openai.com/signup)

### 安裝步驟

**後端（Platform）**

```bash
cd platform
pip install poetry==1.8.5
poetry install
poetry run python -m reworkd_platform
```

**前端（Next.js）**

```bash
cd next
npm install
cp ../.env.example .env
# 編輯 .env 填入你的 API 金鑰
npm run dev
```

然後在瀏覽器中開啟 [http://localhost:3000](http://localhost:3000)。

### 使用 Docker Compose

```bash
docker compose up
```

---

## 🗂️ 專案結構

```
AgentGPT/
├── platform/              # 後端 - FastAPI + LangChain
│   ├── reworkd_platform/  # 應用程式主體
│   │   ├── schemas/       # Pydantic 資料模型
│   │   ├── services/      # 外部服務 (Pinecone, AWS, etc.)
│   │   └── web/api/agent/ # Agent 服務與工具
│   └── tests/             # 測試
├── next/                  # 前端 - Next.js 14 (App Router)
│   ├── src/
│   │   ├── app/           # App Router 頁面
│   │   ├── components/    # React 元件
│   │   ├── hooks/         # 自訂 Hook
│   │   ├── server/        # tRPC Router
│   │   ├── services/      # Agent 服務
│   │   ├── stores/        # Zustand 狀態管理
│   │   └── utils/         # 工具函式
│   └── public/locales/    # i18n 翻譯 (en, zh)
├── db/                    # MySQL 資料庫設定
└── .env.example           # 環境變數範本
```

---

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| **框架** | Next.js 14 (App Router) + FastAPI |
| **語言** | TypeScript 5.7 + Python 3.12 |
| **資料庫** | MySQL 8.0 + Prisma 5 (前端) / SQLAlchemy 2.0 (後端) |
| **認證** | NextAuth.js 4 |
| **樣式** | TailwindCSS 3.4 + HeadlessUI 2 |
| **LLM** | LangChain 0.3 + OpenAI SDK v1 |
| **API** | tRPC 10 (前端) + REST (後端) |
| **容器化** | Docker + Docker Compose |

---

## 🛜 與上游的差異

本專案 Fork 自 [reworkd/AgentGPT](https://github.com/reworkd/AgentGPT)（上游已於 2026 年 1 月存檔），主要現代化升級：

- ✅ **Python 3.12 + Poetry**：Pydantic v2、OpenAI SDK v1、LangChain 0.3
- ✅ **Next.js 14 + App Router**：Pages Router 遷移至 App Router
- ✅ **自訂 i18n**：以原生 i18next 取代 next-i18next
- ✅ **Retry 機制**：OpenAI API 呼叫加入指數退避重試
- ✅ **Docker 現代化**：多階段構建、Node 20、Python 3.12
- ✅ **GPT-4o 支援**：完整支援最新 OpenAI 模型
- ✅ **精簡相依**：移除逾 10 個未使用套件

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/js0935">js0935</a>
</p>
