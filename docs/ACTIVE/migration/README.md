# Guides de Migration - FinancePerso

> Procédures de migration entre versions majeures

---

## 🔄 Migrations Documentées

### [v5-5-dashboard.md](v5-5-dashboard.md)
Migration vers le Dashboard V5.5 (redesign complet).

**De:** Dashboard legacy (avant mars 2026)  
**Vers:** Dashboard V5.5 (light mode, nouvelle architecture)

**Contenu:**
- Changements majeurs
- Procédure de migration
- Rollback possible
- Notes de compatibilité

---

### [notifications-v3.md](notifications-v3.md)
Migration vers le système de notifications V3.

**De:** Notifications V2  
**Vers:** Notifications V3 (persistantes, base de données)

**Contenu:**
- Architecture V3
- Migration des données
- API changes
- Dépannage

---

## 📝 Procédure Standard de Migration

1. **Préparation**
   - Sauvegarde de la base de données
   - Vérification de la version actuelle
   - Lecture du guide de migration

2. **Exécution**
   - Arrêt de l'application
   - Application des migrations
   - Redémarrage et vérification

3. **Validation**
   - Tests fonctionnels
   - Vérification des données
   - Confirmation utilisateurs

4. **Rollback** (si nécessaire)
   - Procédure documentée dans chaque guide

---

## ⚠️ Bonnes Pratiques

- Toujours sauvegarder avant migration
- Tester en environnement de dev d'abord
- Lire les notes de compatibilité
- Ne pas sauter de versions majeures

[Retour à ACTIVE](../README.md) | [Index global](../../INDEX.md)
