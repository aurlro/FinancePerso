# Guide de Migration vers Dashboard V5.5

Ce document décrit la procédure de migration du dashboard legacy vers la nouvelle version V5.5.

## 📋 Prérequis

- ✅ Dashboard Beta testé et validé
- ✅ Sauvegarde de la base de données
- ✅ Tests E2E passés

## 🔄 Procédure de Migration

### Étape 1: Vérification

```bash
python scripts/migrate_to_v5_5.py --check
```

Cette commande affiche l'état actuel des fichiers.

### Étape 2: Tests finaux

```bash
# Lancer les tests
pytest tests/v5_5/ -v
pytest tests/e2e/test_dashboard_beta.py -v
```

### Étape 3: Migration

```bash
python scripts/migrate_to_v5_5.py --apply
```

Cette commande:
1. Crée une sauvegarde de `02_Dashboard.py`
2. Remplace le contenu par la version V5.5
3. Renomme `Dashboard_Beta.py` en `.deprecated`
4. Supprime `99_Test_Dashboard.py`

### Étape 4: Vérification post-migration

```bash
streamlit run app.py
```

Vérifiez:
- [ ] Le dashboard s'affiche correctement
- [ ] Les KPIs sont calculés correctement
- [ ] Le graphique donut fonctionne
- [ ] La liste des transactions s'affiche
- [ ] La navigation fonctionne

## 🚨 Rollback

En cas de problème:

```bash
python scripts/migrate_to_v5_5.py --rollback
```

## 📁 Fichiers concernés

| Fichier | Action | Description |
|---------|--------|-------------|
| `02_Dashboard.py` | Remplacé | Dashboard legacy → V5.5 |
| `Dashboard_Beta.py` | Renommé | Devient `.deprecated` |
| `99_Test_Dashboard.py` | Supprimé | Bac à sable obsolète |
| `02_Dashboard_backup.py` | Créé | Sauvegarde automatique |

## 🆕 Nouvelles fonctionnalités V5.5

### Design
- Light mode moderne (FinCouple)
- Thème épuré avec palette Emerald
- Responsive mobile/tablette

### Composants
- **KPI Cards**: 4 métriques avec variations
- **Donut Chart**: Couleurs par catégorie, total au centre
- **Transaction List**: Icônes par catégorie (25 catégories)
- **Objectifs d'épargne**: Progression visuelle
- **Vue Couple**: Résumé multi-membres

### Performance
- Cache des données avec `@st.cache_data`
- Chargement progressif
- Gestion d'erreurs améliorée

## 🔧 Configuration

### Feature Flag

Dans `modules/constants.py`:

```python
# Avant migration
TEST_DASHBOARD_ENABLED = True  # Active le Dashboard Beta

# Après migration
TEST_DASHBOARD_ENABLED = False  # Désactive (optionnel)
```

### Navigation

Le lien "✨ Tester le nouveau dashboard" dans la sidebar peut être retiré après migration.

## 📝 Checklist post-migration

- [ ] Dashboard accessible à `/Dashboard`
- [ ] Données réelles affichées
- [ ] Filtres fonctionnels
- [ ] Export/Import toujours opérationnel
- [ ] Notifications V3 fonctionnelles
- [ ] Mode couple (si configuré)
- [ ] Tests automatisés passent
- [ ] Documentation mise à jour

## 🐛 Dépannage

### Problème: "Module not found"

**Solution**: Vérifier que tous les fichiers V5.5 sont présents:
```bash
ls modules/ui/v5_5/components/*/
```

### Problème: "Page not found"

**Solution**: Redémarrer Streamlit:
```bash
pkill -f streamlit
streamlit run app.py
```

### Problème: Données non affichées

**Solution**: Vérifier le sélecteur de mois (choisir un mois avec données).

## 📞 Support

En cas de problème persistant:
1. Exécuter le rollback
2. Vérifier les logs Streamlit
3. Consulter `AGENTS.md` pour l'architecture

---

**Date de migration**: _à compléter_
**Effectué par**: _à compléter_
