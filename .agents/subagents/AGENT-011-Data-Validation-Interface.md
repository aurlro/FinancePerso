# AGENT-011: Data Validation Interface Specialist

## 🎯 Mission

Specialiste de l'interface de validation des donnees. Responsable de la conception des ecrans de verification, de categorisation, et de reconciliation. Garant de la precision et de l'efficacite du processus de validation.

---

## 📚 Contexte: Processus de Validation

### Flux de Validation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATION WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │   Import    │───▶│   Detect    │───▶│   Present   │             │
│  │    File     │    │ Duplicates  │    │    List     │             │
│  └─────────────┘    └─────────────┘    └──────┬──────┘             │
│                                                │                     │
│  ┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐             │
│  │   Finalize  │◀───│   Confirm   │◀───│  Categorize │             │
│  │    Save     │    │   Batch     │    │   & Verify  │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Priorites de Validation

```python
VALIDATION_PRIORITIES = {
    'HIGH': {
        'description': 'Requiert attention immediate',
        'conditions': [
            'Montant > 1000 EUR',
            'Nouvelle categorie',
            'Anomalie AI detectee',
            'Possible doublon'
        ],
        'color': '#EF4444'
    },
    'MEDIUM': {
        'description': 'Recommande de verifier',
        'conditions': [
            'Confiance AI < 0.8',
            'Montant inhabituel pour categorie',
            'Nouveau beneficiaire'
        ],
        'color': '#F59E0B'
    },
    'LOW': {
        'description': 'Probablement correct',
        'conditions': [
            'Confiance AI > 0.95',
            'Pattern reconnu',
            'Regle appliquee'
        ],
        'color': '#10B981'
    }
}
```

---

## 🧱 Module 1: Validation Queue

### Liste de Validation

```python
def validation_queue(
    transactions: list[dict],
    on_validate: Callable = None,
    on_skip: Callable = None,
    on_batch_action: Callable = None
):
    """
    Interface de validation par lot.
    
    Args:
        transactions: Transactions a valider
        on_validate: Callback validation individuelle
        on_skip: Callback ignorer
        on_batch_action: Callback action groupee
    """
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        priority_filter = st.selectbox(
            "Priorite",
            ["Toutes", "Haute", "Moyenne", "Basse"]
        )
    with col2:
        category_filter = st.selectbox(
            "Categorie",
            ["Toutes"] + get_all_categories()
        )
    with col3:
        date_filter = st.date_input("Date", value=None)
    
    # Stats
    st.caption(f"{len(transactions)} transactions en attente")
    
    # Selection groupee
    select_all = st.checkbox("Tout selectionner")
    
    # Liste
    selected_ids = []
    
    for tx in transactions:
        # Filtrage
        if priority_filter != "Toutes":
            if tx.get('priority') != priority_filter.upper()[:4]:
                continue
        
        with st.container():
            cols = st.columns([0.05, 0.4, 0.15, 0.15, 0.25])
            
            with cols[0]:
                if st.checkbox("", key=f"select_{tx['id']}", value=select_all):
                    selected_ids.append(tx['id'])
            
            with cols[1]:
                # Info transaction
                priority_color = VALIDATION_PRIORITIES[tx.get('priority', 'LOW')]['color']
                st.markdown(f"""
                    <div style="border-left: 3px solid {priority_color}; padding-left: 0.5rem;">
                        <strong>{tx['label']}</strong><br>
                        <small>{tx['date']} | {tx.get('bank', 'N/A')}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with cols[2]:
                amount_color = 'green' if tx['amount'] > 0 else 'red'
                st.markdown(f":{amount_color}[{tx['amount']:,.2f} €]")
            
            with cols[3]:
                # Categorie suggeree
                st.caption(f"AI: {tx.get('ai_category', '?')}")
                confidence = tx.get('ai_confidence', 0)
                if confidence > 0.9:
                    st.markdown("🟢")
                elif confidence > 0.7:
                    st.markdown("🟡")
                else:
                    st.markdown("🔴")
            
            with cols[4]:
                # Actions rapides
                action_cols = st.columns(3)
                with action_cols[0]:
                    if st.button("✓", key=f"accept_{tx['id']}"):
                        on_validate(tx, tx.get('ai_category'))
                with action_cols[1]:
                    if st.button("✏️", key=f"edit_{tx['id']}"):
                        show_categorization_modal(tx)
                with action_cols[2]:
                    if st.button("⏭️", key=f"skip_{tx['id']}"):
                        on_skip(tx['id'])
            
            st.divider()
    
    # Actions groupees
    if selected_ids:
        st.write(f"📋 {len(selected_ids)} selectionnees")
        batch_cols = st.columns(4)
        with batch_cols[0]:
            if st.button("✓ Valider tout"):
                on_batch_action('validate', selected_ids)
        with batch_cols[1]:
            if st.button("✏️ Categoriser"):
                show_batch_categorization(selected_ids)
        with batch_cols[2]:
            if st.button("🗑️ Ignorer"):
                on_batch_action('skip', selected_ids)
```

### Modal de Categorisation

```python
def show_categorization_modal(transaction: dict):
    """
    Modal pour categoriser une transaction.
    """
    with st.expander(f"📂 Categoriser: {transaction['label'][:30]}...", expanded=True):
        st.write(f"**Montant:** {transaction['amount']:,.2f} €")
        st.write(f"**Date:** {transaction['date']}")
        
        # Suggestions AI
        st.subheader("Suggestions AI")
        suggestions = get_ai_suggestions(transaction)
        
        for i, sugg in enumerate(suggestions[:3]):
            confidence = sugg['confidence']
            color = '#10B981' if confidence > 0.9 else '#F59E0B' if confidence > 0.7 else '#EF4444'
            
            cols = st.columns([0.6, 0.2, 0.2])
            with cols[0]:
                st.write(f"**{sugg['category']}**")
            with cols[1]:
                st.markdown(f"<span style='color: {color};'>{confidence:.0%}</span>", unsafe_allow_html=True)
            with cols[2]:
                if st.button(f"Choisir", key=f"sugg_{transaction['id']}_{i}"):
                    apply_category(transaction['id'], sugg['category'])
                    st.success(f"Categorie appliquee: {sugg['category']}")
        
        # Selection manuelle
        st.subheader("Ou choisir manuellement:")
        manual_cat = st.selectbox(
            "Categorie",
            get_all_categories(),
            key=f"manual_cat_{transaction['id']}"
        )
        
        notes = st.text_area(
            "Notes (optionnel)",
            key=f"notes_{transaction['id']}"
        )
        
        if st.button("Appliquer", key=f"apply_{transaction['id']}"):
            apply_category(transaction['id'], manual_cat, notes)
            st.success("Categorie appliquee!")
```

---

## 🧱 Module 2: Duplicate Detection

### Interface de Resolution

```python
def duplicate_resolver(duplicates: list[dict]):
    """
    Interface pour resoudre les doublons detectes.
    
    Args:
        duplicates: Liste des groupes de doublons
    """
    st.warning(f"⚠️ {len(duplicates)} groupes de doublons detectes")
    
    for i, group in enumerate(duplicates):
        with st.expander(f"Doublon #{i+1}: {group['label'][:30]} ({len(group['items'])} occurrences)"):
            st.write(f"**Label:** {group['label']}")
            st.write(f"**Montant:** {group['amount']:,.2f} €")
            
            # Tableau des occurrences
            df = pd.DataFrame(group['items'])
            st.dataframe(df[['date', 'source', 'status']], use_container_width=True)
            
            # Actions
            action = st.radio(
                "Action",
                [
                    "Conserver toutes (legitimes)",
                    "Conserver la plus recente",
                    "Conserver la premiere",
                    "Fusionner",
                    "Supprimer toutes"
                ],
                key=f"dup_action_{i}"
            )
            
            if st.button("Appliquer", key=f"apply_dup_{i}"):
                resolve_duplicate_group(group['id'], action)
                st.success("Resolu!")
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Interface validation
- Categorisation UX
- Detection doublons UI
- Batch operations
- Reconciliation view

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI


---

## 🌍 Module Additionnel: Advanced Validation UX

### Bulk Editing

```python
"""
Édition en masse avec preview.
"""

def bulk_edit_panel(transaction_ids: list[int]):
    """
    Panneau d'édition en masse.
    
    Args:
        transaction_ids: IDs des transactions à éditer
    """
    st.subheader(f"✏️ Édition de {len(transaction_ids)} transactions")
    
    with st.expander("Champs à modifier", expanded=True):
        # Sélection des champs
        edit_category = st.checkbox("Modifier la catégorie")
        edit_member = st.checkbox("Modifier le membre")
        edit_tags = st.checkbox("Modifier les tags")
        edit_beneficiary = st.checkbox("Modifier le bénéficiaire")
        
        # Valeurs
        if edit_category:
            new_category = st.selectbox(
                "Nouvelle catégorie",
                get_all_categories(),
                key="bulk_category"
            )
        
        if edit_member:
            new_member = st.selectbox(
                "Nouveau membre",
                get_all_members(),
                key="bulk_member"
            )
        
        if edit_tags:
            new_tags = st.text_input(
                "Nouveaux tags (séparés par virgule)",
                key="bulk_tags"
            )
        
        if edit_beneficiary:
            new_beneficiary = st.text_input(
                "Nouveau bénéficiaire",
                key="bulk_beneficiary"
            )
    
    # Preview des changements
    with st.expander("Aperçu des changements"):
        preview_df = get_transactions_preview(transaction_ids)
        
        # Appliquer changements virtuels pour preview
        if edit_category:
            preview_df['category_validated'] = new_category
        
        st.dataframe(preview_df, use_container_width=True)
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Annuler"):
            st.session_state['bulk_edit_ids'] = []
            st.rerun()
    with col2:
        if st.button("✅ Appliquer les changements", type="primary"):
            changes = {}
            if edit_category:
                changes['category_validated'] = new_category
            if edit_member:
                changes['member'] = new_member
            if edit_tags:
                changes['tags'] = new_tags
            if edit_beneficiary:
                changes['beneficiary'] = new_beneficiary
            
            apply_bulk_changes(transaction_ids, changes)
            st.success(f"✅ {len(transaction_ids)} transactions modifiées!")
            st.session_state['bulk_edit_ids'] = []
            st.rerun()
```

### Undo/Redo dans Validation

```python
"""
Système undo/redo pour la validation.
"""

class ValidationHistory:
    """Gère l'historique des actions de validation."""
    
    MAX_HISTORY = 50
    
    def __init__(self):
        if 'validation_history' not in st.session_state:
            st.session_state['validation_history'] = []
            st.session_state['validation_history_index'] = -1
    
    def add_action(self, action: dict):
        """Ajoute une action à l'historique."""
        # Supprimer les actions après l'index courant (redo impossibles)
        self.history = self.history[:self.index + 1]
        
        # Ajouter nouvelle action
        self.history.append({
            'timestamp': datetime.now(),
            'action': action['type'],
            'transaction_ids': action['ids'],
            'previous_state': action['previous'],
            'new_state': action['new']
        })
        
        # Limiter taille
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY:]
        
        self.index = len(self.history) - 1
    
    def undo(self) -> Optional[dict]:
        """Annule la dernière action."""
        if self.index < 0:
            return None
        
        action = self.history[self.index]
        self.index -= 1
        
        # Restaurer état précédent
        return action['previous_state']
    
    def redo(self) -> Optional[dict]:
        """Rétablit une action annulée."""
        if self.index >= len(self.history) - 1:
            return None
        
        self.index += 1
        action = self.history[self.index]
        
        return action['new_state']
    
    @property
    def history(self):
        return st.session_state['validation_history']
    
    @history.setter
    def history(self, value):
        st.session_state['validation_history'] = value
    
    @property
    def index(self):
        return st.session_state['validation_history_index']
    
    @index.setter
    def index(self, value):
        st.session_state['validation_history_index'] = value
    
    def can_undo(self) -> bool:
        return self.index >= 0
    
    def can_redo(self) -> bool:
        return self.index < len(self.history) - 1

def render_undo_redo_buttons(history: ValidationHistory):
    """Affiche les boutons undo/redo."""
    cols = st.columns([1, 1, 8])
    
    with cols[0]:
        if st.button("↩️", disabled=not history.can_undo(), help="Annuler (Ctrl+Z)"):
            state = history.undo()
            if state:
                restore_state(state)
                st.rerun()
    
    with cols[1]:
        if st.button("↪️", disabled=not history.can_redo(), help="Rétablir (Ctrl+Y)"):
            state = history.redo()
            if state:
                restore_state(state)
                st.rerun()
```

### Conflict Resolution

```python
"""
Résolution de conflits de fusion.
"""

def conflict_resolution_dialog(conflicts: list[dict]):
    """
    Interface pour résoudre les conflits de fusion de catégories.
    
    Args:
        conflicts: Liste des conflits {field, local_value, remote_value}
    """
    st.warning(f"⚠️ {len(conflicts)} conflits détectés")
    
    resolutions = {}
    
    for i, conflict in enumerate(conflicts):
        with st.container():
            st.write(f"**{conflict['field']}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Local**")
                st.info(conflict['local_value'])
                if st.button(f"Garder local", key=f"local_{i}"):
                    resolutions[conflict['field']] = conflict['local_value']
            
            with col2:
                st.markdown("**vs**")
                st.write("← →")
            
            with col3:
                st.markdown("**Distant**")
                st.info(conflict['remote_value'])
                if st.button(f"Garder distant", key=f"remote_{i}"):
                    resolutions[conflict['field']] = conflict['remote_value']
            
            # Option personnalisée
            custom = st.text_input("Ou valeur personnalisée", key=f"custom_{i}")
            if custom:
                resolutions[conflict['field']] = custom
            
            st.divider()
    
    return resolutions
```

### Progress Indicators

```python
"""
Indicateurs de progression pour opérations longues.
"""

def batch_progress(current: int, total: int, operation: str = "Traitement"):
    """
    Affiche la progression d'une opération par lot.
    """
    progress = current / total if total > 0 else 0
    
    st.progress(progress)
    st.caption(f"{operation}: {current}/{total} ({progress:.0%})")
    
    # ETA calculation
    if 'batch_start_time' not in st.session_state:
        st.session_state['batch_start_time'] = time.time()
    
    elapsed = time.time() - st.session_state['batch_start_time']
    if current > 0:
        eta_seconds = (elapsed / current) * (total - current)
        eta_str = format_duration(eta_seconds)
        st.caption(f"⏱️ Temps écoulé: {format_duration(elapsed)} | ETA: {eta_str}")

def format_duration(seconds: float) -> str:
    """Formate une durée en secondes."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"

def operation_spinner(operation_name: str):
    """
    Spinner avec étapes pour opération complexe.
    """
    steps = {
        'import': ['Lecture fichier', 'Parsing données', 'Détection doublons', 'Catégorisation', 'Sauvegarde'],
        'export': ['Récupération données', 'Formatage', 'Génération fichier', 'Téléchargement'],
        'backup': ['Dump base', 'Compression', 'Vérification', 'Upload'],
    }
    
    current_step = st.session_state.get('operation_step', 0)
    step_names = steps.get(operation_name, ['Traitement...'])
    
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style=""
                width: 40px;
                height: 40px;
                border: 4px solid #E5E7EB;
                border-top-color: #2563EB;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            "></div>
            <h4>{step_names[min(current_step, len(step_names)-1)]}</h4>
            <p>Étape {current_step + 1}/{len(step_names)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress((current_step + 1) / len(step_names))
```

### Smart Validation Suggestions

```python
"""
Suggestions intelligentes basées sur l'historique.
"""

def smart_suggestions_panel(transaction: dict):
    """
    Panneau de suggestions basé sur l'historique utilisateur.
    """
    with st.expander("💡 Suggestions basées sur votre historique"):
        suggestions = []
        
        # 1. Suggestion par similarité de label
        similar = find_similar_transactions(transaction['label'])
        if similar:
            most_common_category = Counter([s['category_validated'] for s in similar]).most_common(1)[0][0]
            suggestions.append({
                'type': 'category',
                'value': most_common_category,
                'confidence': len([s for s in similar if s['category_validated'] == most_common_category]) / len(similar),
                'reason': f"Catégorisé ainsi {len(similar)} fois précédemment"
            })
        
        # 2. Suggestion par montant
        similar_amount = find_by_amount_range(transaction['amount'] * 0.95, transaction['amount'] * 1.05)
        if similar_amount:
            suggestions.append({
                'type': 'amount_pattern',
                'value': similar_amount[0]['category_validated'],
                'confidence': 0.7,
                'reason': f"Montant similaire à {len(similar_amount)} transactions"
            })
        
        # 3. Suggestion par bénéficiaire
        if transaction.get('beneficiary'):
            by_beneficiary = find_by_beneficiary(transaction['beneficiary'])
            if by_beneficiary:
                suggestions.append({
                    'type': 'beneficiary',
                    'value': by_beneficiary[0]['category_validated'],
                    'confidence': 0.8,
                    'reason': f"Historique avec {transaction['beneficiary']}"
                })
        
        # Afficher suggestions
        for sugg in sorted(suggestions, key=lambda x: x['confidence'], reverse=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{sugg['value']}** - {sugg['reason']}")
                st.caption(f"Confiance: {sugg['confidence']:.0%}")
            with col2:
                if st.button("Appliquer", key=f"sugg_{sugg['type']}"):
                    apply_category(transaction['id'], sugg['value'])
                    st.success(f"Catégorie '{sugg['value']}' appliquée!")
```

### Keyboard Navigation in Validation

```python
"""
Navigation clavier optimisée pour la validation rapide.
"""

def validation_keyboard_handler():
    """
    Handler JavaScript pour navigation clavier dans la validation.
    """
    st.markdown("""
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            let focusedIndex = 0;
            const items = document.querySelectorAll('.validation-item');
            
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return; // Ne pas interférer avec la saisie
                }
                
                switch(e.key) {
                    case 'j': // Next
                    case 'ArrowDown':
                        e.preventDefault();
                        focusedIndex = Math.min(focusedIndex + 1, items.length - 1);
                        items[focusedIndex].focus();
                        break;
                        
                    case 'k': // Previous
                    case 'ArrowUp':
                        e.preventDefault();
                        focusedIndex = Math.max(focusedIndex - 1, 0);
                        items[focusedIndex].focus();
                        break;
                        
                    case 'y': // Accept
                        e.preventDefault();
                        document.querySelector(`#accept-${focusedIndex}`).click();
                        break;
                        
                    case 'n': // Skip/Next
                        e.preventDefault();
                        document.querySelector(`#skip-${focusedIndex}`).click();
                        break;
                        
                    case 'e': // Edit
                        e.preventDefault();
                        document.querySelector(`#edit-${focusedIndex}`).click();
                        break;
                        
                    case 'a': // Select all
                        if (e.ctrlKey) {
                            e.preventDefault();
                            document.querySelector('#select-all').click();
                        }
                        break;
                }
            });
        });
        </script>
    """, unsafe_allow_html=True)

def render_validation_shortcuts_help():
    """Aide pour les raccourcis de validation."""
    with st.expander("⌨️ Raccourcis clavier"):
        st.markdown("""
            | Touche | Action |
            |--------|--------|
            | `j` / `↓` | Transaction suivante |
            | `k` / `↑` | Transaction précédente |
            | `y` | Accepter suggestion |
            | `n` | Ignorer / Passer |
            | `e` | Éditer |
            | `Ctrl+A` | Tout sélectionner |
            | `?` | Afficher l'aide |
        """)
```

---

**Version**: 1.1 - **COMPLÉTÉ**
**Ajouts**: Bulk editing, undo/redo, conflict resolution, progress indicators, smart suggestions, keyboard navigation


---

## 🔗 Module Additionnel: Intégration Categorization (AGENT-005)

### Flow de Validation avec Categorization

```python
"""
Intégration entre AGENT-011 (Validation UI) et AGENT-005 (Categorization).
Ce module définit comment l'interface de validation utilise le moteur de catégorisation.
"""

from modules.categorization import categorize_transaction, apply_rules
from modules.categorization.ai_integration import get_categorization_ai_client

class ValidationCategorizationFlow:
    """
    Orchestration du flow validation → catégorisation.
    
    Ce connecteur assure la coordination entre:
    - AGENT-011: Interface utilisateur de validation
    - AGENT-005: Moteur de catégorisation intelligent
    """
    
    def __init__(self):
        self.ai_client = get_categorization_ai_client()
    
    def process_transaction_validation(
        self,
        transaction: dict,
        user_action: str,  # 'accept_ai', 'manual', 'skip'
        manual_category: str = None
    ) -> dict:
        """
        Process une transaction dans le flow validation.
        
        Args:
            transaction: Données transaction
            user_action: Action choisie par l'utilisateur
            manual_category: Catégorie manuelle si user_action='manual'
        
        Returns:
            Résultat avec category_validated et source
        """
        if user_action == 'accept_ai':
            # Utiliser suggestion AI existante
            return self._accept_ai_suggestion(transaction)
        
        elif user_action == 'manual':
            # Appliquer catégorie manuelle + apprentissage
            return self._apply_manual_category(transaction, manual_category)
        
        elif user_action == 'skip':
            # Marquer comme ignorée
            return self._skip_transaction(transaction)
        
        else:
            raise ValueError(f"Unknown user_action: {user_action}")
    
    def _accept_ai_suggestion(self, transaction: dict) -> dict:
        """Accepte la suggestion AI de la transaction."""
        category = transaction.get('ai_category', 'Inconnu')
        confidence = transaction.get('ai_confidence', 0.0)
        
        # Déterminer source selon confiance
        if confidence >= 0.9:
            source = 'ai_cloud_high_confidence'
        elif confidence >= 0.7:
            source = 'ai_cloud_medium_confidence'
        else:
            source = 'ai_low_confidence'
        
        return {
            'transaction_id': transaction['id'],
            'category_validated': category,
            'confidence': confidence,
            'source': source,
            'action': 'validated_ai'
        }
    
    def _apply_manual_category(self, transaction: dict, category: str) -> dict:
        """Applique catégorie manuelle avec extraction de règle."""
        # Créer potentiellement une règle d'apprentissage
        from modules.categorization.auto_learning import extract_rule_from_validation
        
        should_create_rule, rule_pattern = extract_rule_from_validation(
            transaction['label'],
            category
        )
        
        result = {
            'transaction_id': transaction['id'],
            'category_validated': category,
            'confidence': 1.0,  # Manuel = confiance maximale
            'source': 'manual_validation',
            'action': 'validated_manual'
        }
        
        # Si règle extraite, la proposer
        if should_create_rule:
            result['suggested_rule'] = {
                'pattern': rule_pattern,
                'category': category,
                'priority': 5
            }
        
        return result
    
    def _skip_transaction(self, transaction: dict) -> dict:
        """Marque transaction comme ignorée temporairement."""
        return {
            'transaction_id': transaction['id'],
            'category_validated': 'Inconnu',
            'confidence': 0.0,
            'source': 'skipped',
            'action': 'skipped'
        }
    
    def get_enriched_suggestions(self, transaction: dict) -> list[dict]:
        """
        Récupère suggestions enrichies pour une transaction.
        
        Combine:
        1. Règles existantes (AGENT-005 Rules)
        2. ML local (AGENT-005 Local ML)
        3. AI Cloud (via AGENT-007)
        
        Returns:
            Liste de suggestions avec source et confiance
        """
        suggestions = []
        
        # 1. Règles (100% confiance)
        rule_cat, rule_conf = apply_rules(transaction['label'])
        if rule_cat:
            suggestions.append({
                'category': rule_cat,
                'confidence': rule_conf,
                'source': 'rules',
                'priority': 1
            })
        
        # 2. ML Local
        from modules.categorization.local_ml import LocalTransactionClassifier
        classifier = LocalTransactionClassifier()
        if classifier.is_trained:
            ml_cat, ml_conf = classifier.predict(
                transaction['label'],
                transaction['amount'],
                transaction.get('date')
            )
            if ml_cat and ml_conf >= 0.6:
                suggestions.append({
                    'category': ml_cat,
                    'confidence': ml_conf,
                    'source': 'local_ml',
                    'priority': 2
                })
        
        # 3. AI Cloud (si règles et ML n'ont pas donné résultat haute confiance)
        if not suggestions or max(s['confidence'] for s in suggestions) < 0.9:
            ai_result = self.ai_client.categorize_with_fallback(
                transaction['label'],
                transaction['amount'],
                context={'similar_transactions': []}
            )
            
            if ai_result['category'] != 'Inconnu':
                suggestions.append({
                    'category': ai_result['category'],
                    'confidence': ai_result['confidence'],
                    'source': f"ai_{ai_result['provider_used']}",
                    'priority': 3,
                    'latency_ms': ai_result.get('latency_ms')
                })
        
        # Trier par priorité puis confiance
        suggestions.sort(key=lambda x: (x['priority'], -x['confidence']))
        
        return suggestions

# Helper pour UI
def render_categorization_suggestions(transaction: dict, container):
    """
    Rend les suggestions de catégorisation dans l'UI Streamlit.
    
    Args:
        transaction: Transaction à catégoriser
        container: Container Streamlit (st.container())
    """
    flow = ValidationCategorizationFlow()
    suggestions = flow.get_enriched_suggestions(transaction)
    
    with container:
        st.subheader("💡 Suggestions")
        
        for i, sugg in enumerate(suggestions[:3]):
            # Couleur selon source
            colors = {
                'rules': '🟢',
                'local_ml': '🔵',
                'ai_gemini': '🟡',
                'ai_openai': '🟡',
                'ai_deepseek': '🟡',
                'ai_ollama': '🟠'
            }
            icon = colors.get(sugg['source'], '⚪')
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"{icon} **{sugg['category']}**")
                st.caption(f"Source: {sugg['source']}")
            
            with col2:
                # Barre de confiance
                st.progress(sugg['confidence'])
                st.caption(f"{sugg['confidence']:.0%}")
            
            with col3:
                if st.button("Choisir", key=f"sugg_{transaction['id']}_{i}"):
                    return sugg['category']
        
        # Option manuelle
        st.divider()
        all_categories = get_categories()
        manual = st.selectbox(
            "Ou choisir manuellement:",
            all_categories,
            key=f"manual_{transaction['id']}"
        )
        
        if st.button("Appliquer", key=f"apply_manual_{transaction['id']}"):
            return manual
        
        return None
```

### Matrice de Coordination AGENT-011 ↔ AGENT-005

| Fonctionnalité | AGENT-011 (UI) | AGENT-005 (Engine) | Interaction |
|----------------|----------------|-------------------|-------------|
| Affichage suggestions | Rend widgets | Fournit données | 011 appelle 005 |
| Validation manuelle | Capture input | Extrait règles | 011 notifie 005 |
| Feedback utilisateur | Enregistre action | Met à jour modèle | Event bus |
| Batch validation | Sélection multiple | Applique règles | 011 orchestre 005 |
| Statistiques | Affiche KPIs | Calcule précision | 005 fournit à 011 |

### Events Cross-Agents

```python
# Events émis par AGENT-011 vers AGENT-005
EVENTS_011_TO_005 = {
    'TRANSACTION_VALIDATED': 'Transaction validée manuellement',
    'TRANSACTION_REJECTED': 'Suggestion AI rejetée',
    'RULE_CREATED': 'Nouvelle règle créée depuis validation',
    'BATCH_VALIDATED': 'Validation en lot complétée'
}

# Events émis par AGENT-005 vers AGENT-011
EVENTS_005_TO_011 = {
    'CATEGORIZATION_COMPLETE': 'Catégorisation terminée',
    'RULE_SUGGESTION': 'Suggestion de nouvelle règle',
    'MODEL_UPDATED': 'Modèle ML réentraîné',
    'ACCURACY_ALERT': 'Précision catégorisation faible'
}
```

---

**Version**: 1.2 - **INTÉGRATION AGENT-005 AJOUTÉE**  
**Coordination**: AGENT-005 (Categorization AI Specialist)
