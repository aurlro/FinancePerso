# Suivi des TODOs du Code

**Date de création** : 14 mars 2026  
**Date de mise à jour** : 14 mars 2026  
**Total TODOs** : 11 (7 créées en issues GitHub)

---

## 🔴 HIGH PRIORITY

### TODO-001 : Bouton supprimer lien prêt ✅
- **Fichier** : `modules/ui/couple/loans_view.py:260`
- **Description** : Le bouton pour supprimer un lien entre prêts n'est pas fonctionnel
- **Action** : Implémenter `delete_loan_link()` avec confirmation dialog
- **Issue GitHub** : [#32](https://github.com/aurlro/FinancePerso/issues/32)

### TODO-002 : Récupération DB des objectifs d'épargne V5.5 ✅
- **Fichier** : `modules/ui/v5_5/components/savings_goals.py:118`
- **Description** : Les objectifs d'épargne sont en dur (mockés) au lieu d'être récupérés depuis la base de données
- **Action** : Créer CRUD dans `modules/db/savings_goals.py`
- **Issue GitHub** : [#33](https://github.com/aurlro/FinancePerso/issues/33)

### TODO-003 : Suppression définitive historique ✅
- **Fichier** : `modules/ui/automation/history_tab.py:212`
- **Description** : La suppression définitive des transactions de l'historique n'est pas implémentée
- **Action** : Implémenter `permanently_delete_transactions()`
- **Issue GitHub** : [#34](https://github.com/aurlro/FinancePerso/issues/34)

---

## 🟡 MEDIUM PRIORITY

### TODO-004 : Déconnexion Open Banking ✅
- **Fichier** : `modules/open_banking/sync.py:470`
- **Description** : Déconnexion d'un compte Open Banking non implémentée
- **Action** : Implémenter `disconnect_account()` avec révocation token
- **Issue GitHub** : [#35](https://github.com/aurlro/FinancePerso/issues/35)

### TODO-005 : Fusion de notifications ✅
- **Fichier** : `modules/notifications/ui.py:303`
- **Description** : Fusion des notifications similaires non implémentée
- **Action** : Créer `merge_similar_notifications()` avec compteur
- **Issue GitHub** : [#36](https://github.com/aurlro/FinancePerso/issues/36)

### TODO-006 : Settings utilisateur Dashboard V5.5 ✅
- **Fichier** : `modules/ui/v5_5/pages/dashboard_controller.py:52`
- **Description** : Récupérer les préférences depuis les settings utilisateur
- **Action** : Connecter à `modules/db/settings.py`
- **Issue GitHub** : [#37](https://github.com/aurlro/FinancePerso/issues/37)

---

## 🟢 LOW PRIORITY

### TODO-007 : Alerts zombie/increase ✅
- **Fichier** : `modules/ui/automation/inbox_tab.py:115`
- **Description** : Ajouter alerts pour transactions zombie/augmentation de dépenses
- **Action** : Implémenter détecteurs et affichage
- **Issue GitHub** : [#38](https://github.com/aurlro/FinancePerso/issues/38)

---

## ✅ RÉSOLUS

*Aucun pour le moment*

---

## 📊 STATISTIQUES

| Priorité | Count | Issues créées |
|----------|-------|---------------|
| 🔴 High | 3 | 3/3 ✅ |
| 🟡 Medium | 3 | 3/3 ✅ |
| 🟢 Low | 1 | 1/1 ✅ |
| **Total** | **7** | **7/7** |

---

## 🔗 LIENS UTILES

- [Issues GitHub](https://github.com/aurlro/FinancePerso/issues)
- [Project Board](https://github.com/aurlro/FinancePerso/projects)

---

*Dernière mise à jour : 14/03/2026*
*Script de création : `scripts/create-github-issues.sh`*
