# Fashion Store AI

Online fashion store with Vue frontend, FastAPI backend, MongoDB, and a RAG chatbot (Chroma + OpenAI/Gemini).

## Stack

- Frontend: Vue 3, Vite, Pinia, Vue Router
- Backend: FastAPI, Pydantic, JWT
- Database: MongoDB
- Vector DB: Chroma
- AI core: `backend/ai-core/` (llm, memory, prompts, tool, agents, tests)
- AI: OpenAI or Gemini (RAG), with local demo fallback when API keys are missing
- Deploy: Docker Compose

## AI-core layout

```text
backend/ai-core/
├── agents/          # ShoppingAgent and base agent
├── llm/             # OpenAI/Gemini providers + embeddings
├── memory/          # Chat memory + Chroma vector store
├── prompts/         # System and shopping prompts
├── tool/            # Knowledge retriever/indexer, product search
├── tests/           # Unit tests for AI-core
└── bootstrap.py     # Wire AI-core into FastAPI
```

## Quick start (Docker)

```bash
cd docker
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# start MongoDB locally, then:
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173 and proxies `/api` to the backend.

## Demo accounts

- Admin: `admin@fashionstore.local` / `Admin@123`
- Customer: `customer@fashionstore.local` / `Customer@123`

Promotion codes: `WELCOME10`, `FREESHIP`

## AI configuration

Edit `backend/.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
# or
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

Without API keys the chatbot still works in demo mode using Chroma retrieval + rule-based answers.

## Main features

- Customer: register/login, browse/filter products, cart, checkout, order tracking, AI chat
- Admin: dashboard, products, orders, promotions, FAQ/store knowledge, chatbot reindex
- RAG flow: question → embedding → Chroma context → LLM answer → product suggestions
