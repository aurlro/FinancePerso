# 🎒 Starter Pack - Débuter ce weekend

> Commencer maintenant avec des actions concrètes

---

## ⚡ Ce weekend (4-6 heures)

### Samedi matin (2h): Setup

```bash
# 1. Créer le dossier
mkdir -p ~/Projects/fincouple-pro
cd ~/Projects/fincouple-pro
git init

# 2. Copier les ressources utiles
cp -r /Users/aurelien/Documents/Projets/FinancePerso/modules/categorization* ./reference/
cp -r /Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main/src/lib ./reference/

# 3. Structure
mkdir -p backend/app/{api/routes,core,models,services/ai,db}
mkdir -p frontend/src/{components/ui,features/{auth,dashboard,transactions,budgets,couple,ai},lib}
mkdir -p data

# 4. Initialiser
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose passlib aiosqlite
pip freeze > requirements.txt

cd ../frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npx shadcn-ui@latest init -y
npx shadcn-ui@latest add button card input label
npm install @tanstack/react-query axios react-router-dom react-hook-form zod @hookform/resolvers recharts lucide-react sonner
```

### Samedi après-midi (2h): Hello World

**Backend** (`backend/app/main.py`):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinCouple Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Frontend** (`frontend/src/App.tsx`):
```tsx
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

function App() {
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(r => r.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('error'))
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>FinCouple Pro 🚀</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>API Status: <strong>{status}</strong></p>
          <Button onClick={() => window.location.reload()}>Refresh</Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
```

**Test**:
```bash
# Terminal 1
cd backend
source .venv/bin/activate
python app/main.py

# Terminal 2
cd frontend
npm run dev

# Ouvrir http://localhost:5173
# Devrait afficher "API Status: ok"
```

### Dimanche (2h): Database

**Modèle User** (`backend/app/models/user.py`):
```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, server_default=func.now())
```

**Init DB**:
```bash
cd backend
alembic init migrations
# Éditer alembic.ini → sqlalchemy.url = sqlite:///data/fincouple.db
# Éditer migrations/env.py → target_metadata = Base.metadata

alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## 📁 Structure finale après ce weekend

```
fincouple-pro/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   └── routes/
│   │   ├── 📁 core/
│   │   ├── 📁 models/
│   │   │   └── user.py
│   │   ├── 📁 db/
│   │   │   └── base.py
│   │   └── main.py
│   ├── 📁 migrations/
│   ├── 📁 data/
│   ├── .venv/
│   └── requirements.txt
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   └── ui/
│   │   ├── 📁 features/
│   │   ├── 📁 lib/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── 📁 reference/           # Code source à copier
│   ├── categorization.py
│   └── csv-parser.ts
│
└── README.md
```

---

## ✅ Checklist weekend

- [ ] Dossier créé et git init
- [ ] Backend démarre (`python app/main.py`)
- [ ] Frontend démarre (`npm run dev`)
- [ ] Communication API ↔ Frontend OK
- [ ] Database créée avec Alembic
- [ ] Table users créée
- [ ] Code commité (`git add . && git commit -m "Week 0: Setup"`)

---

## 🎯 Semaine 1 (lundi-vendredi)

### Planning

| Jour | Tâche | Temps |
|------|-------|-------|
| Lundi | Auth backend (register/login/JWT) | 2h |
| Mardi | Auth frontend (pages + context) | 2h |
| Mercredi | Models Transaction + Category | 2h |
| Jeudi | API CRUD Transactions | 2h |
| Vendredi | Liste transactions frontend | 2h |

### Objectif vendredi soir
> Peux créer un compte, me connecter, voir mes transactions

---

## 🆘 Si bloqué

### Problème: CORS error
```python
# Vérifier dans backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Exactement ça
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problème: Alembic ne voit pas les modèles
```python
# Dans migrations/env.py, ajouter:
from app.models import user  # Import tous les modèles
from app.db.base import Base
target_metadata = Base.metadata
```

### Problème: shadcn/ui ne s'installe pas
```bash
# Vérifier Node version
node --version  # Doit être 18+

# Si besoin, utiliser nvm
nvm use 20
```

---

## 📚 Prochaines lectures

1. **Cette semaine**: [FUSION_SOLO_GUIDE.md](./FUSION_SOLO_GUIDE.md) - Semaines 1-8
2. **Quand bloqué**: Documentation FastAPI / React Query
3. **Pour inspiration**: Code FinancePerso dans `reference/`

---

*Pas besoin de tout lire maintenant. Commence, et consulte les docs au besoin.*

**Commence par le Starter Pack ce weekend. Le reste suivra.**

---

*Ready?* `mkdir ~/Projects/fincouple-pro`
