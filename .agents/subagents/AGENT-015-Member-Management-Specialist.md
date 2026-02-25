# AGENT-015: Member Management Specialist

## 🎯 Mission

Spécialiste de la gestion multi-utilisateurs et des permissions. Responsable de la gestion des membres du foyer, de l'attribution des transactions, et de la personnalisation par utilisateur.

---

## 📚 Contexte: Architecture Multi-Utilisateur

### Modèle de Données

```python
# modules/members/models.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MemberRole(Enum):
    OWNER = "owner"           # Propriétaire du compte
    ADMIN = "admin"           # Admin (partenaire)
    MEMBER = "member"         # Membre régulier
    GUEST = "guest"           # Accès limité

class MemberType(Enum):
    HOUSEHOLD = "household"   # Membre du foyer
    EXTERNAL = "external"     # Bénéficiaire externe

@dataclass
class Member:
    """Membre du foyer."""
    id: int
    name: str
    email: Optional[str] = None
    role: MemberRole = MemberRole.MEMBER
    member_type: MemberType = MemberType.HOUSEHOLD
    color: str = "#2563EB"    # Couleur pour graphiques
    avatar: Optional[str] = None
    default_category: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class MemberMapping:
    """Mapping pour attribuer automatiquement les transactions."""
    id: int
    member_id: int
    mapping_type: str         # 'card_suffix', 'account', 'pattern'
    mapping_value: str        # Les 4 digits, nom compte, ou regex
    priority: int = 1
    created_at: datetime = None

@dataclass
class MemberPermissions:
    """Permissions d'un membre."""
    member_id: int
    can_view_all: bool = True
    can_edit_own: bool = True
    can_edit_all: bool = False
    can_manage_budgets: bool = False
    can_export: bool = False
    can_delete: bool = False
    allowed_categories: List[str] = field(default_factory=list)
```

---

## 🧱 Module 1: Member Management

### Gestion des Membres

```python
# modules/members/manager.py

class MemberManager:
    """Gestionnaire des membres."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_member(
        self,
        name: str,
        email: str = None,
        role: MemberRole = MemberRole.MEMBER,
        color: str = None
    ) -> Member:
        """
        Crée un nouveau membre.
        
        Args:
            name: Nom du membre
            email: Email optionnel
            role: Rôle dans le foyer
            color: Couleur pour les graphiques
        
        Returns:
            Member créé
        """
        if color is None:
            color = self._assign_color()
        
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT INTO members (name, email, role, color, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, role.value, color, datetime.now()))
        
        self.db.commit()
        
        logger.info(f"Membre créé: {name} ({role.value})")
        
        return Member(
            id=cursor.lastrowid,
            name=name,
            email=email,
            role=role,
            color=color
        )
    
    def assign_transaction_to_member(
        self,
        transaction_id: int,
        member_id: int,
        manual: bool = True
    ):
        """Attribue une transaction à un membre."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            UPDATE transactions 
            SET member = (SELECT name FROM members WHERE id = ?),
                member_assigned_at = ?,
                member_assignment_manual = ?
            WHERE id = ?
        """, (member_id, datetime.now(), manual, transaction_id))
        
        self.db.commit()
    
    def auto_assign_transactions(self, transaction_ids: List[int] = None):
        """
        Attribue automatiquement les transactions aux membres.
        Basé sur les mappings (carte, compte, pattern).
        """
        cursor = self.db.cursor()
        
        # Récupérer tous les mappings actifs
        cursor.execute("""
            SELECT mm.*, m.name as member_name
            FROM member_mappings mm
            JOIN members m ON mm.member_id = m.id
            ORDER BY mm.priority DESC
        """)
        mappings = cursor.fetchall()
        
        # Construire requête
        where_clause = "WHERE member IS NULL"
        params = []
        
        if transaction_ids:
            placeholders = ','.join(['?' for _ in transaction_ids])
            where_clause += f" AND id IN ({placeholders})"
            params.extend(transaction_ids)
        
        cursor.execute(f"SELECT * FROM transactions {where_clause}", params)
        transactions = cursor.fetchall()
        
        assigned_count = 0
        
        for tx in transactions:
            assigned_member = None
            
            for mapping in mappings:
                if mapping['mapping_type'] == 'card_suffix':
                    if tx.get('card_suffix') == mapping['mapping_value']:
                        assigned_member = mapping['member_name']
                        break
                
                elif mapping['mapping_type'] == 'account':
                    if tx.get('account_label') == mapping['mapping_value']:
                        assigned_member = mapping['member_name']
                        break
                
                elif mapping['mapping_type'] == 'pattern':
                    import re
                    if re.search(mapping['mapping_value'], tx['label'], re.IGNORECASE):
                        assigned_member = mapping['member_name']
                        break
            
            if assigned_member:
                cursor.execute("""
                    UPDATE transactions 
                    SET member = ?, member_assigned_at = ?, member_assignment_manual = 0
                    WHERE id = ?
                """, (assigned_member, datetime.now(), tx['id']))
                assigned_count += 1
        
        self.db.commit()
        logger.info(f"{assigned_count} transactions attribuées automatiquement")
        
        return assigned_count
    
    def get_member_statistics(self, member_id: int, months: int = 12) -> dict:
        """
        Statistiques par membre.
        
        Returns:
            Dépenses, revenus, top catégories
        """
        cursor = self.db.cursor()
        
        cursor.execute("SELECT name FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return None
        
        member_name = member['name']
        
        # Dépenses totales
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) as expenses,
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as income
            FROM transactions
            WHERE member = ?
            AND date >= date('now', '-? months')
        """, (member_name, months))
        
        totals = cursor.fetchone()
        
        # Top catégories
        cursor.execute("""
            SELECT category_validated, SUM(ABS(amount)) as total
            FROM transactions
            WHERE member = ?
            AND amount < 0
            AND date >= date('now', '-? months')
            GROUP BY category_validated
            ORDER BY total DESC
            LIMIT 5
        """, (member_name, months))
        
        top_categories = [
            {'category': row['category_validated'], 'amount': row['total']}
            for row in cursor.fetchall()
        ]
        
        return {
            'member_id': member_id,
            'member_name': member_name,
            'period_months': months,
            'total_expenses': totals['expenses'],
            'total_income': totals['income'],
            'balance': totals['income'] - totals['expenses'],
            'top_categories': top_categories
        }
    
    def _assign_color(self) -> str:
        """Attribue une couleur unique au membre."""
        colors = [
            '#2563EB',  # Blue
            '#10B981',  # Green
            '#F59E0B',  # Amber
            '#EF4444',  # Red
            '#8B5CF6',  # Purple
            '#EC4899',  # Pink
            '#06B6D4',  # Cyan
            '#84CC16',  # Lime
        ]
        
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM members")
        count = cursor.fetchone()['count']
        
        return colors[count % len(colors)]
```

---

## 🧱 Module 2: Permissions System

### Gestion des Permissions

```python
# modules/members/permissions.py

class PermissionManager:
    """Gestionnaire des permissions."""
    
    ROLE_PERMISSIONS = {
        MemberRole.OWNER: {
            'can_view_all': True,
            'can_edit_own': True,
            'can_edit_all': True,
            'can_manage_budgets': True,
            'can_manage_members': True,
            'can_export': True,
            'can_delete': True,
            'can_configure': True
        },
        MemberRole.ADMIN: {
            'can_view_all': True,
            'can_edit_own': True,
            'can_edit_all': True,
            'can_manage_budgets': True,
            'can_manage_members': True,
            'can_export': True,
            'can_delete': False,
            'can_configure': True
        },
        MemberRole.MEMBER: {
            'can_view_all': True,
            'can_edit_own': True,
            'can_edit_all': False,
            'can_manage_budgets': False,
            'can_manage_members': False,
            'can_export': False,
            'can_delete': False,
            'can_configure': False
        },
        MemberRole.GUEST: {
            'can_view_all': False,
            'can_edit_own': False,
            'can_edit_all': False,
            'can_manage_budgets': False,
            'can_manage_members': False,
            'can_export': False,
            'can_delete': False,
            'can_configure': False
        }
    }
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_permissions(self, member_id: int) -> dict:
        """Récupère les permissions d'un membre."""
        cursor = self.db.cursor()
        
        cursor.execute("SELECT role FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return self.ROLE_PERMISSIONS[MemberRole.GUEST]
        
        role = MemberRole(member['role'])
        return self.ROLE_PERMISSIONS.get(role, self.ROLE_PERMISSIONS[MemberRole.GUEST])
    
    def can_edit_transaction(self, member_id: int, transaction_member: str) -> bool:
        """Vérifie si peut éditer une transaction."""
        perms = self.get_permissions(member_id)
        
        if perms['can_edit_all']:
            return True
        
        if perms['can_edit_own']:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT name FROM members WHERE id = ?",
                (member_id,)
            )
            member_name = cursor.fetchone()['name']
            return transaction_member == member_name
        
        return False
    
    def can_view_category(self, member_id: int, category: str) -> bool:
        """Vérifie si peut voir une catégorie."""
        perms = self.get_permissions(member_id)
        
        if perms['can_view_all']:
            return True
        
        # Vérifier restrictions spécifiques
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT allowed_categories FROM member_permissions WHERE member_id = ?
        """, (member_id,))
        
        result = cursor.fetchone()
        if result and result['allowed_categories']:
            allowed = result['allowed_categories'].split(',')
            return category in allowed
        
        return False
```

---

## 🧱 Module 3: Personalization

### Préférences Utilisateur

```python
# modules/members/preferences.py

class UserPreferences:
    """Gestion des préférences utilisateur."""
    
    DEFAULT_PREFERENCES = {
        'currency': 'EUR',
        'date_format': 'DD/MM/YYYY',
        'number_format': 'european',  # 1.234,56
        'language': 'fr',
        'theme': 'light',
        'dashboard_layout': 'default',
        'default_page': 'home',
        'notifications_enabled': True,
        'email_alerts': False,
        'weekly_report': True,
        'budget_alert_threshold': 0.8,
        'ai_suggestions_enabled': True,
        'auto_categorize_threshold': 0.85,
        'items_per_page': 50
    }
    
    def __init__(self, db_connection, member_id: int):
        self.db = db_connection
        self.member_id = member_id
    
    def get(self, key: str, default=None):
        """Récupère une préférence."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT value FROM member_preferences 
            WHERE member_id = ? AND key = ?
        """, (self.member_id, key))
        
        result = cursor.fetchone()
        
        if result:
            import json
            return json.loads(result['value'])
        
        return self.DEFAULT_PREFERENCES.get(key, default)
    
    def set(self, key: str, value):
        """Définit une préférence."""
        import json
        
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO member_preferences 
            (member_id, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        """, (self.member_id, key, json.dumps(value), datetime.now()))
        
        self.db.commit()
    
    def get_all(self) -> dict:
        """Récupère toutes les préférences."""
        prefs = self.DEFAULT_PREFERENCES.copy()
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT key, value FROM member_preferences WHERE member_id = ?
        """, (self.member_id,))
        
        import json
        for row in cursor.fetchall():
            prefs[row['key']] = json.loads(row['value'])
        
        return prefs
```

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI


---

## 🔧 Module Additionnel: Tests & Coordination

### Tests Unitaires

```python
# tests/unit/test_members.py
"""
Tests du module gestion des membres.
"""

import pytest
from datetime import datetime
from modules.members.manager import MemberManager
from modules.members.permissions import PermissionManager
from modules.members.preferences import UserPreferences

class TestMemberManager:
    """Tests de la gestion des membres."""
    
    def test_create_member(self, db_connection):
        """Test création d'un membre."""
        manager = MemberManager(db_connection)
        
        member = manager.create_member(
            name="Alice",
            email="alice@example.com",
            role=MemberRole.MEMBER
        )
        
        assert member.name == "Alice"
        assert member.email == "alice@example.com"
        assert member.color is not None  # Couleur auto-assignée
    
    def test_auto_assign_by_card_suffix(self, db_connection):
        """Test attribution automatique par suffixe carte."""
        manager = MemberManager(db_connection)
        
        # Créer membre avec mapping carte
        member = manager.create_member(name="Bob")
        manager.create_mapping(member.id, 'card_suffix', '1234')
        
        # Créer transaction avec ce suffixe
        tx_id = insert_transaction(db_connection, {
            'card_suffix': '1234',
            'label': 'Test',
            'amount': -50.0
        })
        
        # Lancer auto-assign
        assigned = manager.auto_assign_transactions([tx_id])
        
        assert assigned == 1
        
        # Vérifier attribution
        tx = get_transaction(db_connection, tx_id)
        assert tx['member'] == 'Bob'
    
    def test_member_statistics(self, db_connection, sample_transactions):
        """Test calcul statistiques par membre."""
        manager = MemberManager(db_connection)
        
        member = manager.create_member(name="Charlie")
        
        # Insérer transactions pour ce membre
        for tx in sample_transactions:
            tx['member'] = 'Charlie'
            insert_transaction(db_connection, tx)
        
        stats = manager.get_member_statistics(member.id, months=12)
        
        assert stats['member_name'] == 'Charlie'
        assert 'total_expenses' in stats
        assert 'total_income' in stats
        assert 'top_categories' in stats
    
    def test_unique_color_assignment(self, db_connection):
        """Test assignation couleurs uniques."""
        manager = MemberManager(db_connection)
        
        colors = set()
        for i in range(5):
            member = manager.create_member(name=f"Member{i}")
            colors.add(member.color)
        
        # Tous doivent avoir des couleurs différentes
        assert len(colors) == 5

class TestPermissionManager:
    """Tests du système de permissions."""
    
    def test_owner_permissions(self, db_connection):
        """Test permissions propriétaire."""
        perm_manager = PermissionManager(db_connection)
        
        # Créer owner
        member = MemberManager(db_connection).create_member(
            name="Owner",
            role=MemberRole.OWNER
        )
        
        perms = perm_manager.get_permissions(member.id)
        
        assert perms['can_edit_all'] == True
        assert perms['can_manage_members'] == True
        assert perms['can_delete'] == True
    
    def test_guest_permissions(self, db_connection):
        """Test permissions invité."""
        perm_manager = PermissionManager(db_connection)
        
        member = MemberManager(db_connection).create_member(
            name="Guest",
            role=MemberRole.GUEST
        )
        
        perms = perm_manager.get_permissions(member.id)
        
        assert perms['can_view_all'] == False
        assert perms['can_edit_own'] == False
    
    def test_can_edit_transaction(self, db_connection):
        """Test vérification édition transaction."""
        perm_manager = PermissionManager(db_connection)
        
        member = MemberManager(db_connection).create_member(
            name="User",
            role=MemberRole.MEMBER
        )
        
        # Membre peut éditer sa propre transaction
        assert perm_manager.can_edit_transaction(member.id, 'User') == True
        
        # Membre ne peut pas éditer transaction d'un autre
        assert perm_manager.can_edit_transaction(member.id, 'Other') == False

class TestUserPreferences:
    """Tests des préférences utilisateur."""
    
    def test_default_preferences(self, db_connection):
        """Test valeurs par défaut."""
        member = MemberManager(db_connection).create_member(name="User")
        prefs = UserPreferences(db_connection, member.id)
        
        assert prefs.get('currency') == 'EUR'
        assert prefs.get('language') == 'fr'
        assert prefs.get('theme') == 'light'
    
    def test_set_preference(self, db_connection):
        """Test définition préférence."""
        member = MemberManager(db_connection).create_member(name="User")
        prefs = UserPreferences(db_connection, member.id)
        
        prefs.set('theme', 'dark')
        
        assert prefs.get('theme') == 'dark'
    
    def test_get_all_preferences(self, db_connection):
        """Test récupération toutes préférences."""
        member = MemberManager(db_connection).create_member(name="User")
        prefs = UserPreferences(db_connection, member.id)
        
        all_prefs = prefs.get_all()
        
        assert 'currency' in all_prefs
        assert 'language' in all_prefs
        assert 'theme' in all_prefs
```

### Imports et Configuration

```python
# modules/members/__init__.py
"""
Module members - Imports standardisés.
"""

import logging
import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)

# Exports
from .manager import MemberManager, MemberRole, MemberType
from .permissions import PermissionManager
from .preferences import UserPreferences

__all__ = [
    'MemberManager',
    'PermissionManager',
    'UserPreferences',
    'MemberRole',
    'MemberType',
    'logger'
]
```

### Coordination avec AGENT-016 (Notifications)

```python
"""
Coordination entre AGENT-015 (Members) et AGENT-016 (Notifications).
"""

class MemberNotificationCoordinator:
    """
    Connecteur entre gestion des membres et notifications.
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.member_manager = MemberManager(db_connection)
        # AGENT-016 - NotificationEngine
        from modules.notifications.engine import NotificationEngine
        self.notification_engine = NotificationEngine(db_connection)
    
    def notify_member_of_transaction(self, member_id: int, transaction: dict):
        """
        Notifie un membre d'une transaction le concernant.
        """
        member = self.member_manager.get_member(member_id)
        
        if not member or not member.email:
            return
        
        # Créer notification via AGENT-016
        self.notification_engine.create_notification(
            member_id=member_id,
            type=NotificationType.TRANSACTION_ALERT,
            title="Nouvelle transaction",
            message=f"{transaction['label']}: {transaction['amount']:.2f} EUR",
            data={
                'transaction_id': transaction['id'],
                'amount': transaction['amount'],
                'category': transaction.get('category_validated')
            },
            channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        )
    
    def notify_member_of_budget_alert(self, member_id: int, alert: dict):
        """
        Notifie un membre d'une alerte budgétaire.
        """
        self.notification_engine.create_notification(
            member_id=member_id,
            type=NotificationType.BUDGET_ALERT,
            title=f"Budget {alert['status']}",
            message=alert['message'],
            priority=NotificationPriority.HIGH if alert['status'] == 'exceeded' else NotificationPriority.NORMAL,
            data=alert
        )
```

---

**Version**: 1.1 - **TESTS ET COORDINATION AJOUTÉS**  
**Coordination**: AGENT-016 (Notifications)
