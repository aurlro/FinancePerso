# ADR 001: Choix de SQLite comme base de données

## Statut

✅ Accepté (2024-01-15)

## Contexte

FinancePerso a besoin d'une base de données pour stocker :
- Transactions bancaires (10 000+ par utilisateur)
- Catégories, membres, règles
- Configurations utilisateur

## Options considérées

### 1. SQLite (choisi)
**Avantages:**
- Zero-config (fichier local)
- Pas de serveur requis
- Parfait pour app desktop/personnelle
- Bonnes performances pour < 1M lignes
- Python standard library

**Inconvénients:**
- Pas de multi-écriture concurrente
- Limité à 1 utilisateur local

### 2. PostgreSQL
**Avantages:**
- Robuste, scalable
- Multi-utilisateurs
- Fonctions avancées

**Inconvénients:**
- Nécessite installation serveur
- Overkill pour app personnelle
- Complexité déploiement

### 3. JSON/CSV files
**Avantages:**
- Ultra simple
- Lisible par humain

**Inconvénients:**
- Pas de requêtes SQL
- Pas d'intégrité référentielle
- Lenteur avec volume

## Décision

**SQLite** choisi pour:
1. Simplicité déploiement (utilisateur final)
2. Aucune maintenance requise
3. Performances suffisantes pour usage personnel
4. Portabilité (fichier unique)

## Conséquences

- ✅ Déploiement ultra-simple
- ✅ Backup = copier un fichier
- ✅ Pas de Docker nécessaire
- ⚠️ Limité à usage local single-user
- ⚠️ Pas de sync cloud native

## Notes

Si besoin multi-utilisateurs/cloud dans le futur:
- PostgreSQL avec SQLAlchemy (même ORM)
- Migration transparente possible
- SQLite reste option offline
