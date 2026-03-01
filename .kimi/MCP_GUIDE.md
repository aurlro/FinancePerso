# 🚀 Guide MCP - FinancePerso

## Configuration créée

3 nouveaux serveurs MCP ont été configurés dans `~/.config/kimi/mcp.json` :

| Serveur | Usage | Commande |
|---------|-------|----------|
| **sqlite** | Requêtes SQL directes sur ta base | `uvx mcp-server-sqlite` |
| **filesystem** | Exploration fichiers avancée | `npx @modelcontextprotocol/server-filesystem` |
| **fetch** | Requêtes web/API | `uvx mcp-server-fetch` |

---

## ⚡ Comment utiliser

### 1. Redémarrer Kimi Code CLI
Les nouveaux serveurs seront disponibles après redémarrage de Kimi.

### 2. Utilisation via requêtes naturelles

**Exemples de prompts qui fonctionneront :**

```
"Exécute cette requête SQL sur ma base : SELECT COUNT(*) FROM transactions"

"Liste mes 10 plus grosses dépenses du mois"

"Combien de transactions en pending ?"

"Montre-moi l'évolution de mes dépenses par catégorie"

"Recherche toutes les transactions Amazon"

"Vérifie si j'ai dépassé mon budget ce mois-ci"
```

---

## 📁 Fichiers créés

```
.kimi/
├── MCP_GUIDE.md              # Ce guide
└── mcp_queries_examples.sql  # 10 requêtes SQL prêtes à l'emploi
```

---

## 🎯 Requêtes SQL prêtes à l'emploi

Voir `mcp_queries_examples.sql` pour :
- Stats globales (dépenses/revenus/balance)
- Top catégories par mois
- Transactions à valider
- Évolution mensuelle (12 mois)
- Détection d'anomalies
- Stats par membre
- Budget vs Réel
- Recherche par mot-clé
- Corbeille
- Stats IA (taux de confiance)

---

## 🔧 Cas d'usage avancés

### Analyse rapide sans coder
```
"Quelle est ma catégorie de dépense la plus élevée ce mois ?"
```

### Debug de données
```
"Y a-t-il des transactions avec un montant négatif ?"
```

### Validation import
```
"Combien de transactions ont été importées hier ?"
```

### Export ciblé
```
"Exporte mes transactions du mois de janvier 2024 en CSV"
```

---

## 📝 Notes

- La base SQLite est en **lecture seule** par défaut pour la sécurité
- Les requêtes sont exécutées directement sur `Data/finance.db`
- Pas besoin d'écrire du Python pour analyser tes données !

---

**Configuration créée le :** 2026-03-01  
**Par :** Kimi Code CLI 🤖
