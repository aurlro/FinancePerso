# 01 - Vision : Pourquoi FinCouple Pro ?

## 🎯 Objectif

Combiner :
- **UX moderne** de FinCouple (React, mobile-first)
- **Fonctionnalités avancées** de FinancePerso (IA, projections, couple)

**Tagline**: *"La simplicité de FinCouple, la puissance de FinancePerso"*

---

## 📊 Analyse comparative

| Domaine | FinancePerso | FinCouple | Gagnant |
|---------|-------------|-----------|---------|
| **Fonctionnalités** | ⭐⭐⭐⭐⭐ (50+) | ⭐⭐⭐ (8) | FinancePerso |
| **UX/UI** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | FinCouple |
| **Mobile** | ⭐⭐ | ⭐⭐⭐⭐⭐ | FinCouple |
| **IA/ML** | ⭐⭐⭐⭐⭐ | ⭐⭐ | FinancePerso |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | FinCouple |
| **Privacy** | ⭐⭐⭐⭐⭐ | ⭐⭐ | FinancePerso |

---

## 🏗️ Architecture cible

```
┌────────────────────────────────────────────────────────────┐
│  REACT (Frontend)                                          │
│  ├── Dashboard quotidien                                   │
│  ├── Import & Validation                                   │
│  ├── Budgets & Objectifs                                   │
│  └── Vue Couple                                            │
├────────────────────────────────────────────────────────────┤
│  FASTAPI (Backend)                                         │
│  ├── Auth JWT                                              │
│  ├── Business Logic                                        │
│  ├── IA (catégorisation)                                   │
│  └── WebSocket temps réel                                  │
├────────────────────────────────────────────────────────────┤
│  STREAMLIT (Admin)                                         │
│  ├── Audit avancé                                          │
│  ├── Configuration IA                                      │
│  └── Projections Monte Carlo                               │
├────────────────────────────────────────────────────────────┤
│  SQLITE (Local)                                            │
│  ├── Privacy-first                                         │
│  └── Chiffrement optionnel                                 │
└────────────────────────────────────────────────────────────┘
```

---

## 👥 Parcours utilisateur

### Alice (mobile, quotidien)
1. Dashboard "Reste à vivre"
2. Notification dépense inhabituelle
3. 1 clic pour catégoriser
4. Badge débloqué

### Bob (desktop, import)
1. Import CSV banque
2. Auto-catégorisation IA
3. Validation batch rapide

### Ensemble (planification)
1. Vue répartition perso/joint
2. Discussion prêts
3. Objectif épargne

### Week-end (admin)
1. Audit règles IA (Streamlit)
2. Projections scénarios
3. Export comptable

---

## 📈 Résultat attendu

- **12 écrans principaux** (vs 22 Streamlit)
- **~40k lignes** (vs 65k Python)
- **Experience mobile native**
- **Fonctionnalités couple avancées**
- **100% offline possible**

---

[→ Roadmap détaillée : 02_PLAN.md](./02_PLAN.md)
