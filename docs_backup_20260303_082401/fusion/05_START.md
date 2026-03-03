# 05 - Guide de Démarrage

> Actions concrètes pour démarrer immédiatement

---

## ✅ Prérequis

- [ ] Avoir lu [01_VISION.md](./01_VISION.md)
- [ ] Avoir lu [02_PLAN.md](./02_PLAN.md)
- [ ] Node.js 18+ installé
- [ ] Python 3.12+ installé
- [ ] Docker installé (optionnel mais recommandé)

---

## 🚀 Démarrage (Jour 1)

### 1. Créer le repository

```bash
mkdir fincouple-pro && cd fincouple-pro
git init

# Structure
cat > README.md << 'EOF'
# FinCouple Pro
Fusion FinancePerso + FinCouple
EOF
```

### 2. Setup Docker Compose

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/fincouple.db

  web:
    build: ./apps/web
    ports:
      - "3000:80"
    depends_on:
      - api

  admin:
    build: ./apps/admin
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    depends_on:
      - api
EOF
```

### 3. Setup Backend FastAPI

```bash
mkdir -p api/src/{models,routers,services,core}
cd api

# Virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies
pip install fastapi uvicorn sqlalchemy alembic pydantic[email] python-jose[cryptography] passlib[bcrypt] python-multipart

# Requirements
pip freeze > requirements.txt

# Main file
cat > src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinCouple Pro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/")
def root():
    return {"message": "FinCouple Pro API", "docs": "/docs"}
EOF
```

### 4. Setup Frontend React

```bash
mkdir -p apps/web && cd apps/web

# Create Vite app
npm create vite@latest . -- --template react-ts

# Dependencies
npm install @tanstack/react-query axios react-router-dom zustand
npm install -D tailwindcss postcss autoprefixer

# Tailwind
npx tailwindcss init -p

# shadcn/ui
npx shadcn-ui@latest init

# Test
npm run dev
```

---

## 📋 Semaine 1 Checklist

### Jour 1-2 : Setup
- [ ] Repository créé
- [ ] Docker Compose fonctionnel
- [ ] FastAPI hello world
- [ ] React hello world

### Jour 3-4 : Database
- [ ] SQLAlchemy models
- [ ] Alembic migrations
- [ ] Tables créées

### Jour 5 : Auth
- [ ] JWT implementation
- [ ] Register/Login endpoints
- [ ] Frontend auth context
- [ ] Protected routes

---

## 🛠️ Commandes utiles

### Backend
```bash
cd api
source .venv/bin/activate

# Dev server
uvicorn src.main:app --reload --port 8000

# Tests
pytest

# Database migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### Frontend
```bash
cd apps/web

# Dev server
npm run dev

# Build
npm run build

# Tests
npm test

# Lint
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up -d

# Logs
docker-compose logs -f api
docker-compose logs -f web

# Reset
docker-compose down -v
rm -rf data/*.db
docker-compose up -d
```

---

## 🔍 Vérification

### API fonctionne ?
```bash
curl http://localhost:8000/health
# {"status": "ok", "version": "0.1.0"}
```

### Frontend fonctionne ?
```bash
curl http://localhost:3000
# HTML de l'app React
```

### Database ?
```bash
ls data/
# fincouple.db
```

---

## 📚 Ressources

### Documentation externe
- [FastAPI](https://fastapi.tiangolo.com)
- [React Query](https://tanstack.com/query/latest)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)

### Projets source
- FinancePerso: `/Users/aurelien/Documents/Projets/FinancePerso`
- FinCouple: `/Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main`

---

## ❓ Problèmes courants

### Port déjà utilisé
```bash
# Trouver process
lsof -i :8000
# Kill
kill -9 <PID>
```

### Docker permission
```bash
# Linux
sudo usermod -aG docker $USER
# Re-login
```

### Node modules corrompus
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## ✅ Prochaines étapes

Une fois le setup terminé :

1. [Implémenter auth complète](../03_SPECS.md#auth)
2. [Créer models database](../03_SPECS.md#database-schema)
3. [CRUD transactions](../03_SPECS.md#transactions)
4. [Dashboard React](../04_UI_UX.md)

---

*Ready? Set. Go! 🚀*
