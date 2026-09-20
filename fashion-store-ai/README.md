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

## Project Structure

```text
fashion-store-ai/
├── backend/
│   ├── .env                 # Cấu hình môi trường Backend
│   ├── .env.example         # Mẫu cấu hình Backend (FastAPI, MongoDB, AI, CORS)
│   ├── Dockerfile           # Dockerfile Backend
│   ├── requirements.txt     # Python dependencies
│   ├── ai-core/             # Module AI & RAG
│   └── app/                 # FastAPI routes & services
├── frontend/
│   ├── .env                 # Cấu hình môi trường Frontend
│   ├── .env.example         # Mẫu cấu hình Frontend (Vite port, API proxy)
│   ├── Dockerfile           # Dockerfile Frontend
│   ├── nginx.conf           # Nginx reverse proxy
│   ├── package.json         # Node dependencies
│   └── src/                 # Vue 3 source code
├── docker/
│   └── ...                  # Cấu hình phụ trợ Docker
└── docker-compose.yml       # Khởi chạy fullstack toàn bộ hệ thống
```

## Quick start (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Local development

### 1. Backend

```bash
cd backend
# Copy file cấu hình môi trường
cp .env.example .env

# Cài đặt môi trường ảo Python
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt

# Khởi động backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
# Copy file cấu hình môi trường
cp .env.example .env

# Cài đặt thư viện & chạy dev server
npm install
npm run dev
```

Frontend chạy tại http://localhost:5173 và proxy các request `/api` sang backend (cổng 8000).

## Demo accounts & Seed data

- **Admin (Quản trị)**: `Admin@fashion.vn` / `Admin@123`
- **Khách hàng (Tenant/Customer)**: `Tenant@fashion.vn` / `Tenant@123`

Chạy script tạo lại toàn bộ dữ liệu mẫu bất kỳ lúc nào:
```bash
# Windows PowerShell:
./seed_demo.ps1

# Linux / macOS / Bash:
./seed_demo.sh

# Hoặc qua Docker:
docker compose exec backend python seed_demo.py --reset
```

Promotion codes: `WELCOME10`, `FREESHIP`, `FASHION2026`, `VIP50`

## AI configuration

Chỉnh sửa trong `backend/.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
# hoặc
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

Nếu không có API key, chatbot vẫn hoạt động ở chế độ demo (fallback tìm kiếm sản phẩm & thông tin qua ChromaDB).
