# AGENT-000: Orchestrator

## 🎯 Mission

Orchestrateur central de tous les agents spécialisés de FinancePerso. Responsable de la coordination entre agents, de la résolution de conflits, et de la cohérence globale du système. Garde-fou ultime garantissant que tous les agents travaillent harmonieusement.

---

## 📚 Contexte: Architecture Multi-Agents

### Philosophie
> "Un agent seul est rapide, des agents coordonnés sont invincibles."

### Cartographie des Agents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT ORCHESTRATOR                                   │
│                         (Coordination & Supervision)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 1: INFRASTRUCTURE (Foundation)                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ AGENT-001   │  │ AGENT-002   │  │ AGENT-003   │                          │
│  │ Database    │◄─┤ Security    │◄─┤ DevOps      │                          │
│  │ Architect   │  │ Guardian    │  │ Engineer    │                          │
│  └──────┬──────┘  └─────────────┘  └─────────────┘                          │
│         │                                                                    │
│         ▼                                                                    │
│  LAYER 2: CORE BUSINESS (Heart)                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ AGENT-004   │◄─┤ AGENT-005   │◄─┤ AGENT-006   │                          │
│  │ Transaction │  │ Categorize  │  │ Analytics   │                          │
│  │ Engine      │  │ AI          │  │ Dashboard   │                          │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘                          │
│         │                │                                                   │
│         ▼                ▼                                                   │
│  LAYER 3: AI SERVICES (Brain)                                               │
│  ┌─────────────┐  ┌─────────────┐                                           │
│  │ AGENT-007   │◄─┤ AGENT-008   │                                           │
│  │ AI Provider │  │ AI Features │                                           │
│  │ Manager     │  │ Specialist  │                                           │
│  └──────┬──────┘  └─────────────┘                                           │
│         │                                                                    │
│         ▼                                                                    │
│  LAYER 4: UI/UX (Interface)                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ AGENT-009   │◄─┤ AGENT-010   │◄─┤ AGENT-011   │                          │
│  │ UI Component│  │ Navigation  │  │ Validation  │                          │
│  │ Architect   │  │ Experience  │  │ Interface   │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
│                                                                              │
│  LAYER 5: QUALITY (Assurance)                                               │
│  ┌─────────────┐  ┌─────────────┐                                           │
│  │ AGENT-012   │◄─┤ AGENT-013   │                                           │
│  │ Test Auto   │  │ QA Integration│                                          │
│  └─────────────┘  └─────────────┘                                           │
│                                                                              │
│  LAYER 6: SPECIALIZED (Features)                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ AGENT-014   │◄─┤ AGENT-015   │◄─┤ AGENT-016   │                          │
│  │ Budget/     │  │ Member      │  │ Notification│                          │
│  │ Wealth      │  │ Management  │  │ System      │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Matrice de Dépendances

| Agent | Dépend de | Fournit à |
|-------|-----------|-----------|
| AGENT-001 | - | 002, 003, 004, 005, 006, 014, 015, 016 |
| AGENT-002 | - | Tous (sécurité transverse) |
| AGENT-003 | - | Tous (infrastructure) |
| AGENT-004 | 001, 002 | 005, 006, 011 |
| AGENT-005 | 001, 004, 007 | 006, 008, 011 |
| AGENT-006 | 001, 004, 005 | 009, 010 |
| AGENT-007 | 002, 003 | 005, 008 |
| AGENT-008 | 001, 004, 007 | 006, 009, 016 |
| AGENT-009 | 006, 008 | 010, 011 |
| AGENT-010 | 006, 009 | 011 |
| AGENT-011 | 004, 005, 009 | 016 |
| AGENT-012 | 001-011 | - |
| AGENT-013 | 001-011 | - |
| AGENT-014 | 001, 004, 006 | 009, 016 |
| AGENT-015 | 001, 002 | 004, 006, 016 |
| AGENT-016 | 001, 014, 015 | 009, 010 |

---

## 🔧 Protocoles de Coordination

### 1. Protocol: Database Change (001)

```python
"""
Quand AGENT-001 modifie le schéma, notification à tous les agents concernés.
"""

def on_database_schema_changed(changes: list[dict]):
    """
    Handler appelé par AGENT-001 après migration.
    
    Args:
        changes: Liste des changements {table, column, action}
    """
    affected_agents = set()
    
    for change in changes:
        table = change['table']
        
        # Déterminer agents impactés
        if table == 'transactions':
            affected_agents.update(['004', '005', '006', '011'])
        elif table == 'categories':
            affected_agents.update(['005', '006', '009'])
        elif table == 'members':
            affected_agents.update(['004', '006', '015', '016'])
        elif table == 'budgets':
            affected_agents.update(['014', '016'])
        elif table == 'notifications':
            affected_agents.update(['016'])
    
    # Invalider caches
    for agent_id in affected_agents:
        notify_agent(agent_id, {
            'event': 'SCHEMA_CHANGED',
            'changes': changes
        })
```

### 2. Protocol: Security Event (002)

```python
"""
Quand AGENT-002 détecte une menace ou applique une politique.
"""

def on_security_alert(alert: dict):
    """
    Handler pour alertes sécurité.
    """
    severity = alert['severity']
    
    if severity == 'critical':
        # Bloquer toutes les opérations sensibles
        broadcast_to_all({
            'event': 'SECURITY_LOCKDOWN',
            'reason': alert['message'],
            'duration_minutes': 30
        })
    
    elif severity == 'high':
        # Forcer re-authentification
        notify_agents(['004', '015'], {
            'event': 'REAUTH_REQUIRED',
            'reason': alert['message']
        })
    
    elif severity == 'warning':
        # Logger seulement
        log_security_event(alert)
```

### 3. Protocol: AI Provider Switch (007)

```python
"""
Quand AGENT-007 switch de provider (fallback).
"""

def on_ai_provider_switched(from_provider: str, to_provider: str, reason: str):
    """
    Handler pour changement de provider IA.
    """
    # Notifier agents qui utilisent l'IA
    notify_agents(['005', '008'], {
        'event': 'AI_PROVIDER_SWITCHED',
        'from': from_provider,
        'to': to_provider,
        'reason': reason,
        'latency_impact': get_latency_impact(to_provider)
    })
    
    # Ajuster timeouts dans UI
    notify_agent('009', {
        'event': 'ADJUST_TIMEOUTS',
        'new_timeout_ms': get_provider_timeout(to_provider)
    })
```

### 4. Protocol: Transaction Import (004)

```python
"""
Quand AGENT-004 importe de nouvelles transactions.
"""

def on_transactions_imported(count: int, by_member: str = None):
    """
    Handler post-import.
    """
    # Déclencher catégorisation
    notify_agent('005', {
        'event': 'TRANSACTIONS_PENDING',
        'count': count
    })
    
    # Mettre à jour analytics
    notify_agent('006', {
        'event': 'REFRESH_DASHBOARD'
    })
    
    # Mettre à jour badge validation
    notify_agent('010', {
        'event': 'UPDATE_BADGE',
        'page': 'validation',
        'count': count
    })
    
    # Notifier membres concernés
    if by_member:
        notify_agent('016', {
            'event': 'SEND_NOTIFICATION',
            'type': 'transactions_imported',
            'recipient': by_member,
            'data': {'count': count}
        })
```

### 5. Protocol: Budget Alert (014)

```python
"""
Quand AGENT-014 détecte un dépassement budgétaire.
"""

def on_budget_alert(alert: BudgetAlert):
    """
    Handler pour alertes budget.
    """
    # Mettre à jour UI dashboard
    notify_agent('009', {
        'event': 'SHOW_ALERT_BANNER',
        'severity': alert.alert_type,
        'message': alert.message
    })
    
    # Envoyer notification
    notify_agent('016', {
        'event': 'CREATE_NOTIFICATION',
        'type': 'budget_alert',
        'priority': 'high' if alert.alert_type == 'exceeded' else 'normal',
        'title': f"Budget {alert.alert_type}",
        'message': alert.message,
        'data': {
            'category': alert.category,
            'percentage': alert.percentage_used
        }
    })
```

---

## 🚨 Gestion des Conflits

### Types de Conflits

```python
class ConflictType(Enum):
    SCHEMA_MISMATCH = "schema_mismatch"      # Agent utilise vieux schéma
    API_INCOMPATIBLE = "api_incompatible"    # Changement interface cassant
    CIRCULAR_DEP = "circular_dependency"     # Dépendance circulaire
    RACE_CONDITION = "race_condition"        # Accès concurrent
    SECURITY_VIOLATION = "security_violation"  # Non-respect sécurité
```

### Résolution Automatique

```python
def resolve_conflict(conflict: dict) -> dict:
    """
    Résout un conflit entre agents.
    
    Returns:
        Plan de résolution
    """
    conflict_type = conflict['type']
    
    if conflict_type == ConflictType.SCHEMA_MISMATCH:
        return resolve_schema_mismatch(conflict)
    
    elif conflict_type == ConflictType.API_INCOMPATIBLE:
        return resolve_api_incompatibility(conflict)
    
    elif conflict_type == ConflictType.CIRCULAR_DEP:
        return resolve_circular_dependency(conflict)
    
    elif conflict_type == ConflictType.RACE_CONDITION:
        return resolve_race_condition(conflict)
    
    elif conflict_type == ConflictType.SECURITY_VIOLATION:
        # Bloquer immédiatement
        return {
            'action': 'BLOCK',
            'reason': conflict['details'],
            'notify': ['002', '003']  # Security + DevOps
        }

def resolve_schema_mismatch(conflict: dict) -> dict:
    """Résout un mismatch de schéma."""
    agent_id = conflict['agent']
    expected = conflict['expected_schema']
    actual = conflict['actual_schema']
    
    # Forcer mise à jour agent
    return {
        'action': 'FORCE_UPDATE',
        'agent': agent_id,
        'instructions': f"Mettre à jour pour schéma v{actual['version']}",
        'breaking_changes': detect_breaking_changes(expected, actual)
    }

def resolve_circular_dependency(conflict: dict) -> dict:
    """Résout une dépendance circulaire."""
    cycle = conflict['cycle']  # ['004', '005', '007', '004']
    
    # Identifier point de rupture optimal
    # Généralement: casser au niveau de l'abstraction la plus haute
    break_point = find_weakest_link(cycle)
    
    return {
        'action': 'REFACTOR',
        'break_at': break_point,
        'solution': 'Introduire interface/abstraction',
        'new_dependency': 'AGENT-000 (orchestrator)'
    }
```

---

## 📋 Checklist de Coordination

### Avant Modification

- [ ] Identifier tous les agents impactés
- [ ] Vérifier compatibilité avec AGENT-002 (Security)
- [ ] Vérifier compatibilité avec AGENT-001 (Database)
- [ ] Mettre à jour dépendances dans cette documentation

### Pendant Modification

- [ ] Suivre protocol de coordination approprié
- [ ] Maintenir backward compatibility si possible
- [ ] Documenter breaking changes

### Après Modification

- [ ] Notifier agents dépendants
- [ ] Mettre à jour tests (AGENT-012)
- [ ] Valider avec QA (AGENT-013)
- [ ] Mettre à jour documentation

---

## 🔍 Monitoring & Diagnostics

### Health Check Global

```python
def system_health_check() -> dict:
    """
    Vérifie la santé de tous les agents.
    
    Returns:
        Rapport de santé global
    """
    report = {
        'timestamp': datetime.now(),
        'agents': {},
        'conflicts': [],
        'recommendations': []
    }
    
    for agent_id in AGENT_REGISTRY:
        agent_health = check_agent_health(agent_id)
        report['agents'][agent_id] = agent_health
        
        if agent_health['status'] != 'healthy':
            report['recommendations'].append({
                'agent': agent_id,
                'issue': agent_health['issue'],
                'action': agent_health['recommended_action']
            })
    
    # Détecter conflits
    report['conflicts'] = detect_active_conflicts()
    
    return report
```

### Diagnostic de Conflit

```python
def diagnose_conflict(agent_a: str, agent_b: str) -> dict:
    """
    Diagnostique un conflit entre deux agents.
    """
    return {
        'common_dependencies': find_common_deps(agent_a, agent_b),
        'interface_mismatches': check_interface_compatibility(agent_a, agent_b),
        'schema_versions': {
            agent_a: get_agent_schema_version(agent_a),
            agent_b: get_agent_schema_version(agent_b)
        },
        'last_coordination': get_last_coordination_time(agent_a, agent_b)
    }
```

---

## 📚 Références Croisées

### Quick Reference: Qui contacter pour...

| Besoin | Agent Primaire | Agents Secondaires |
|--------|----------------|-------------------|
| Nouvelle table DB | **001** | 002, 003 |
| Chiffrement données | **002** | 001, 015 |
| Pipeline CI/CD | **003** | 002, 012 |
| Import fichier | **004** | 001, 005, 011 |
| Catégorisation | **005** | 004, 007, 008 |
| Nouveau graphique | **006** | 009, 010 |
| Provider IA | **007** | 002, 005, 008 |
| Anomalies ML | **008** | 005, 006, 016 |
| Composant UI | **009** | 006, 008, 010 |
| Navigation | **010** | 009, 011 |
| Validation données | **011** | 004, 005, 009 |
| Nouveau test | **012** | Agent concerné |
| Test E2E | **013** | 009, 010, 011 |
| Budget/épargne | **014** | 001, 006, 016 |
| Membres | **015** | 001, 002, 004 |
| Notification | **016** | 014, 015 |

---

**Version**: 1.0  
**Date**: 2026-02-25  
**Statut**: PRÊT À L'EMPLOI  
**Agents Supervisés**: 001-016


---

## 🔍 RAPPORT D'AUDIT DÉTAILLÉ

### Problèmes Identifiés et Résolutions

#### 🔴 CRITIQUE: Incohérences Schema DB

**Problème**: AGENT-001 mentionne `transaction_history` mais table incomplète dans schéma.
**Impact**: Pas de traçabilité des modifications.
**Résolution**: Compléter schéma dans AGENT-001.

#### 🔴 CRITIQUE: EventBus Orphelin

**Problème**: AGENT-001 mentionne EventBus mais aucun autre agent ne l'implémente.
**Impact**: Découplage non fonctionnel.
**Résolution**: Ajouter EventBus aux agents concernés (004, 005, 014, 016).

#### 🟡 MAJEUR: Categorization sans référence AI Provider

**Problème**: AGENT-005 (Categorization) utilise AI Cloud mais ne référence pas AGENT-007.
**Impact**: Pas de fallback si AI down.
**Résolution**: Mettre à jour AGENT-005 pour utiliser AIProvider de AGENT-007.

#### 🟡 MAJEUR: Validation UI sans lien Categorization

**Problème**: AGENT-011 (Validation) ne référence pas AGENT-005 pour la catégorisation.
**Impact**: Incohérence dans le flow validation.
**Résolution**: Ajouter référence croisée AGENT-005 → AGENT-011.

#### 🟢 MINEUR: Imports manquants dans code examples

**Problème**: Plusieurs agents ont des snippets sans imports.
**Agents concernés**: 014, 015, 016
**Résolution**: Ajouter imports standardisés.

#### 🟢 MINEUR: Logger non défini

**Problème**: `logger` utilisé mais jamais importé dans certains snippets.
**Résolution**: Ajouter `import logging; logger = logging.getLogger(__name__)`.

---

## 📋 MATRICE DE COHÉRENCE VÉRIFIÉE

| Critère | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 | 011 | 012 | 013 | 014 | 015 | 016 |
|---------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Mission claire | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Architecture | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Code examples | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Cross-refs | ⚠️ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |
| Error handling | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Tests | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

Légende: ✅ Complet | ⚠️ Partiel | ❌ Manquant

---

## 🎯 PLAN D'ACTION PRIORITAIRE

### Phase 1: Corrections Critiques (Immédiat)
1. ✅ Créer AGENT-000 Orchestrator (FAIT)
2. 🔄 Mettre à jour AGENT-005 pour référencer AGENT-007
3. 🔄 Mettre à jour AGENT-011 pour référencer AGENT-005

### Phase 2: Cohérence (Court terme)
4. 🔄 Ajouter imports manquants dans AGENT-014, 015, 016
5. 🔄 Ajouter section tests dans AGENT-014, 015, 016
6. 🔄 Créer module EventBus commun

### Phase 3: Optimisation (Moyen terme)
7. 🔄 Créer diagrammes d'architecture à jour
8. 🔄 Générer index des agents
9. 🔄 Créer templates de contribution

---

**Prochaine étape recommandée**: Appliquer les corrections des agents 005, 011, 014, 015, 016.


---

## 🔌 NOUVEAUX AGENTS 017-021 - Intégration et Coordination

*(Ajout post-création des agents spécialisés ETL, Open Banking, Performance, Accessibility, et Documentation)*

### 6. Protocol: Data Pipeline Import (017)

```python
"""
Quand AGENT-017 importe des données massives.
"""

def on_data_import_started(import_id: str, source_type: str, estimated_records: int):
    """
    Handler début d'import.
    """
    # Notifier AGENT-016 pour afficher progression
    notify_agent('016', {
        'event': 'IMPORT_STARTED',
        'import_id': import_id,
        'message': f"Import {source_type} démarré ({estimated_records} records estimés)"
    })
    
    # Mettre à jour AGENT-010 (badge import)
    notify_agent('010', {
        'event': 'UPDATE_BADGE',
        'page': 'import',
        'status': 'in_progress'
    })

def on_data_import_completed(import_id: str, result: dict):
    """
    Handler fin d'import.
    """
    # Déclencher catégorisation
    if result.get('records_imported', 0) > 0:
        notify_agent('005', {
            'event': 'TRANSACTIONS_PENDING',
            'count': result['records_imported'],
            'source': 'import',
            'import_id': import_id
        })
    
    # Optimiser DB via AGENT-019 si gros volume
    if result.get('records_imported', 0) > 1000:
        notify_agent('019', {
            'event': 'OPTIMIZE_DATABASE',
            'reason': 'post_import',
            'record_count': result['records_imported']
        })
    
    # Notification utilisateur
    notify_agent('016', {
        'event': 'IMPORT_COMPLETED',
        'import_id': import_id,
        'result': result
    })

def on_data_import_failed(import_id: str, error: str):
    """
    Handler échec d'import.
    """
    notify_agent('016', {
        'event': 'IMPORT_FAILED',
        'import_id': import_id,
        'error': error,
        'priority': 'high'
    })
```

### 7. Protocol: Open Banking Sync (018)

```python
"""
Quand AGENT-018 synchronise des transactions bancaires.
"""

def on_bank_sync_completed(connection_id: str, result: dict):
    """
    Handler fin de sync bancaire.
    """
    # Nouvelles transactions
    if result.get('transactions_new', 0) > 0:
        # Catégoriser
        notify_agent('005', {
            'event': 'TRANSACTIONS_PENDING',
            'count': result['transactions_new'],
            'source': 'banking_sync',
            'connection_id': connection_id
        })
        
        # Notification utilisateur
        notify_agent('016', {
            'event': 'NEW_TRANSACTIONS',
            'title': f"🏦 {result['transactions_new']} nouvelles transactions",
            'message': "Importées depuis votre banque",
            'data': {'connection_id': connection_id, 'count': result['transactions_new']}
        })
        
        # Mettre à jour dashboard
        notify_agent('006', {
            'event': 'REFRESH_DASHBOARD'
        })

def on_bank_connection_expired(connection_id: str, bank_name: str):
    """
    Handler expiration connexion bancaire.
    """
    notify_agent('016', {
        'event': 'CONNECTION_EXPIRED',
        'title': f"🔔 Connexion {bank_name} expirée",
        'message': "Veuillez vous reconnecter pour continuer la synchronisation",
        'priority': 'high',
        'data': {'connection_id': connection_id, 'action': 'reconnect'}
    })

def on_bank_token_refresh_failed(connection_id: str):
    """
    Handler échec refresh token.
    """
    # Forcer reconnexion
    notify_agent('018', {
        'event': 'FORCE_RECONNECT',
        'connection_id': connection_id
    })
```

### 8. Protocol: Performance Alert (019)

```python
"""
Quand AGENT-019 détecte des problèmes de performance.
"""

def on_performance_degraded(metric: str, value: float, threshold: float):
    """
    Handler dégradation performance.
    """
    severity = 'warning' if value < threshold * 2 else 'critical'
    
    # Notifier monitoring
    notify_agent('015', {
        'event': 'PERFORMANCE_ALERT',
        'metric': metric,
        'value': value,
        'threshold': threshold,
        'severity': severity
    })
    
    # Actions auto si critique
    if severity == 'critical':
        if metric == 'memory_usage':
            # Déclencher garbage collection
            notify_agent('019', {
                'event': 'EMERGENCY_GC'
            })
        elif metric == 'query_time':
            # Activer cache agressif
            notify_agent('003', {
                'event': 'ENABLE_AGGRESSIVE_CACHING'
            })

def on_slow_query_detected(query: str, duration_ms: float):
    """
    Handler requête lente détectée.
    """
    # Logger pour analyse
    logger.warning(f"Slow query detected: {duration_ms:.1f}ms - {query[:100]}")
    
    # Suggérer index si pattern récurrent
    notify_agent('001', {
        'event': 'SUGGEST_INDEX',
        'query_pattern': query[:200],
        'duration_ms': duration_ms
    })
```

### 9. Protocol: Accessibility Audit (020)

```python
"""
Quand AGENT-020 détecte des problèmes d'accessibilité.
"""

def on_a11y_violation_detected(violation: dict):
    """
    Handler violation accessibilité.
    """
    severity = violation.get('severity', 'minor')
    
    if severity in ['critical', 'serious']:
        # Bloquer le déploiement si violation critique
        notify_agent('003', {
            'event': 'BLOCK_DEPLOYMENT',
            'reason': 'a11y_critical_violation',
            'violation': violation
        })
    
    # Logger dans monitoring
    notify_agent('015', {
        'event': 'A11Y_VIOLATION',
        'severity': severity,
        'rule': violation.get('rule'),
        'element': violation.get('element')
    })

def on_a11y_audit_completed(report: dict):
    """
    Handler fin d'audit accessibilité.
    """
    score = report.get('validity_score', 0)
    
    if score < 90:
        # Créer ticket amélioration
        notify_agent('021', {
            'event': 'CREATE_IMPROVEMENT_TICKET',
            'title': f"Améliorer accessibilité (score: {score:.1f}%)",
            'report': report
        })
```

### 10. Protocol: Documentation Update (021)

```python
"""
Quand AGENT-021 met à jour la documentation.
"""

def on_documentation_published(doc_type: str, path: str, version: str):
    """
    Handler publication documentation.
    """
    # Notifier équipe
    notify_agent('016', {
        'event': 'DOCS_UPDATED',
        'title': f"📚 Documentation {doc_type} mise à jour",
        'message': f"Version {version} publiée",
        'data': {'path': path, 'version': version}
    })

def on_changelog_generated(version: str, changelog: str):
    """
    Handler génération changelog.
    """
    # Mettre à jour release notes
    notify_agent('003', {
        'event': 'UPDATE_RELEASE_NOTES',
        'version': version,
        'changelog': changelog
    })
```

---

## 📊 Matrice de Dépendances Étendue (001-021)

| Agent | Dépend de | Fournit à |
|-------|-----------|-----------|
| **017** | 001, 005 | 005, 006, 016, 019 |
| **018** | 002, 005 | 005, 006, 016 |
| **019** | 001, 003 | 001, 003, 006, 015 |
| **020** | 009, 010 | 009, 010, 015 |
| **021** | 000, 017, 018 | 003, 015 |

---

## 🎯 Quick Reference: Agents 017-021

| Besoin | Agent Primaire | Agents Secondaires |
|--------|----------------|-------------------|
| Import fichier | **017** | 001, 005, 016 |
| Migration historique | **017** | 001, 005 |
| Connexion bancaire | **018** | 002, 005, 016 |
| Synchronisation auto | **018** | 005, 016 |
| Optimisation DB | **019** | 001, 003 |
| Cache tuning | **019** | 003 |
| Audit accessibilité | **020** | 009, 010 |
| ARIA/composants | **020** | 009, 010 |
| Changelog | **021** | 000, 003 |
| API docs | **021** | 018 |

---

**Version**: 2.0  
**Date**: 2026-02-25  
**Agents Supervisés**: 001-021 (22 agents complets)
