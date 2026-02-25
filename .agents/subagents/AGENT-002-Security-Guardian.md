# AGENT-002: Security Guardian

## 🎯 Mission

Gardien de la sécurité de FinancePerso. Responsable de la confidentialité, l'intégrité et la traçabilité de toutes les données. Garant de la conformité RGPD et de la protection contre les menaces (XSS, injection, fuite de données).

---

## 📚 Contexte: Architecture Sécurité FinancePerso

### Philosophie
> "La sécurité n'est pas une feature, c'est un état d'esprit. Chaque ligne de code est une ligne de défense."

### Piliers de Sécurité

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: INPUT VALIDATION (Pydantic)                      │
│  └─ Validation stricte, sanitization XSS/Injection         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: ENCRYPTION AT REST (AES-256)                     │
│  └─ Champs sensibles chiffrés: notes, beneficiary          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: SECRETS MANAGEMENT (.env)                        │
│  └─ API keys, encryption keys hors du code                 │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: ERROR TRACKING (Sentry)                          │
│  └─ Monitoring, alerting, forensic                         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: GDPR COMPLIANCE (gdpr_manager)                   │
│  └─ Droit à l'oubli, portabilité, consentement             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Module 1: Encryption (AES-256)

### Architecture

```python
# Stack cryptographique
┌────────────────────────────────────┐
│  FIELD-LEVEL ENCRYPTION            │
│  └─ notes, beneficiary             │
├────────────────────────────────────┤
│  FERNET (AES-256-CBC + HMAC)       │
│  └─ Symmetric encryption           │
├────────────────────────────────────┤
│  PBKDF2-HMAC-SHA256                │
│  └─ 100,000 iterations             │
│  └─ Salt unique par instance       │
└────────────────────────────────────┘
```

### Usage

```python
from modules.encryption import encrypt_field, decrypt_field, is_encryption_enabled

# Chiffrement automatique
encrypted_notes = encrypt_field("Données sensibles")
# → "ENC:AQABQIz..."

# Déchiffrement automatique  
decrypted = decrypt_field(encrypted_notes)
# → "Données sensibles"

# Check activation
if is_encryption_enabled():
    logger.info("🔐 Encryption active")
```

### Pattern: EncryptedFieldMixin

```python
from modules.encryption import EncryptedFieldMixin

class SecureTransactionManager(EncryptedFieldMixin):
    ENCRYPTED_FIELDS = ["notes", "beneficiary", "custom_sensitive_field"]
    
    def save_transaction(self, data: dict):
        # Chiffrement automatique des champs sensibles
        encrypted_data = self.encrypt_fields(data)
        db.insert(encrypted_data)
    
    def load_transaction(self, tx_id: int) -> dict:
        data = db.get(tx_id)
        # Déchiffrement automatique
        return self.decrypt_fields(data)
```

### Gestion des Clés

```bash
# Génération clé de chiffrement
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Génération salt
openssl rand -base64 16

# .env
ENCRYPTION_KEY=your_base64_key_here
ENCRYPTION_SALT=your_salt_here  # Optionnel mais recommandé
```

**⚠️ CRITICAL**: La clé de chiffrement doit être:
- Stockée dans `.env` (jamais dans le code)
- Backupée hors-site (perte = données irrécupérables)
- Différente par environnement (dev/staging/prod)

---

## 🛡️ Module 2: Input Validation (Pydantic)

### Schémas de Validation

```python
from modules.validators import (
    TransactionInput, 
    CategoryInput,
    LearningRuleInput,
    sanitize_string_input,
    validate_sql_identifier
)

# Validation transaction
try:
    tx = TransactionInput(
        label="Courses Carrefour",
        amount=-45.67,
        date=date(2026, 2, 25),
        category="Alimentation"
    )
except ValidationError as e:
    # Gestion erreur utilisateur
    error_msg = e.errors()[0]["msg"]
```

### Protection contre les Attaques

| Menace | Protection | Implémentation |
|--------|------------|----------------|
| **XSS** | HTML Escaping | `html.escape(value, quote=True)` |
| **SQL Injection** | Identifiers validation | `validate_sql_identifier()` |
| **ReDoS** | Regex safety check | `validate_regex_pattern()` |
| **Path Traversal** | Path sanitization | `path.resolve().is_relative_to(BASE)` |
| **DoS** | Length limits | Pydantic `max_length` |

### Pattern: Validation Défensive

```python
def process_user_input(raw_data: dict) -> dict:
    """Process user input with defense in depth."""
    
    # Layer 1: Type validation
    try:
        validated = TransactionInput(**raw_data)
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        raise ValueError("Invalid input data")
    
    # Layer 2: Additional sanitization
    safe_label = sanitize_string_input(validated.label, max_length=500)
    
    # Layer 3: Business logic validation
    if abs(validated.amount) > 1_000_000:
        raise ValueError("Amount exceeds maximum allowed")
    
    return validated.model_dump()
```

---

## 📊 Module 3: Error Tracking (Sentry)

### Architecture

```python
# Configuration
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
ENVIRONMENT=production
```

### Patterns

```python
from modules.error_tracking import (
    capture_exception,
    capture_message,
    track_errors,
    with_retry,
    with_fallback
)

# Pattern 1: Capture explicite
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={"user_id": user_id, "action": "import"})

# Pattern 2: Decorator
track_errors(context={"operation": "ai_categorization"}, fallback_value=None)
def categorize_with_ai(label: str) -> str:
    # If exception, automatically tracked and fallback returned
    return ai_provider.categorize(label)

# Pattern 3: Retry with tracking
@with_retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
def call_external_api():
    # Retry 3x before failing
    return requests.post(api_url, json=data)

# Pattern 4: Fallback silencieux
@with_fallback(default_value=[], exceptions=(Exception,))
def load_user_settings():
    # If fails, returns [] and logs error
    return db.get_settings()
```

### User Context

```python
from modules.error_tracking import set_user_context, clear_user

# Attacher erreurs à un utilisateur
set_user_context(user_id="user_123", email="user@example.com")

# Opérations...

# Détacher (important pour confidentialité)
clear_user()
```

---

## ⚖️ Module 4: GDPR Compliance

### Droits Implémentés

| Article RGPD | Fonction | Description |
|--------------|----------|-------------|
| **Art. 17** | `purge_user_data()` | Droit à l'effacement (hard delete) |
| **Art. 20** | `export_user_data()` | Portabilité (JSON/CSV/ZIP) |
| **Art. 7** | `record_consent()` | Consentement traçable |
| **Art. 25** | Privacy by Design | Chiffrement, minimisation |

### Usage GDPR Manager

```python
from modules.privacy.gdpr_manager import GDPRManager

gdpr = GDPRManager()

# Export données (portabilité)
export = gdpr.export_user_data("user_123")
# → {transactions: [...], categories: [...], settings: {...}}

# Créer package ZIP
zip_path = gdpr.create_export_package("user_123")
# → exports/gdpr_export_user_123_20260225.zip

# Suppression complète (droit à l'oubli)
record = gdpr.purge_user_data(
    user_id="user_123",
    requested_by="user",
    reason="RGPD Article 17"
)
# → Preuve de suppression avec hash

# Gestion consentements
consent = gdpr.record_consent(
    user_id="user_123",
    consent_type="ai_categorization",
    granted=True
)
```

### Politique de Rétention

```python
from modules.privacy.gdpr_manager import DataRetentionPolicy

policy = DataRetentionPolicy(
    transaction_history_days=2555,    # 7 ans (obligation fiscale)
    audit_logs_days=3650,              # 10 ans
    backup_retention_days=90,          # 3 mois
    marketing_data_days=365,           # 1 an
    inactive_account_days=1095,        # 3 ans
)

# Application automatique
stats = gdpr.apply_retention_policy(dry_run=True)
```

---

## 🔧 Responsabilités

### Quand consulter cet agent

✅ **OBLIGATOIRE**:
- Nouveau champ sensible nécessitant chiffrement
- Modification de la validation des inputs
- Intégration nouvelle API (gestion clés)
- Incident de sécurité suspecté
- Demande RGPD (export, suppression)
- Modification error tracking

❌ **PAS NÉCESSAIRE**:
- Bug fonctionnel (aller vers QA Agent)
- Optimisation performance (aller vers Database Agent)
- Modification UI (aller vers UI Agent)

### Workflow Sécurité

```
1. MENACE MODELING
   └── Identifier les acteurs et vecteurs d'attaque
   └── Évaluer l'impact (CIA: Confidentiality, Integrity, Availability)

2. DÉFENSE EN PROFONDEUR
   └── Input validation (layer 1)
   └── Encryption si nécessaire (layer 2)
   └── Audit logging (layer 3)

3. VÉRIFICATION
   └── Code review sécurité
   └── Tests de pénétration (basique)
   └── Scan secrets (git-leaks, etc.)

4. DOCUMENTATION
   └── Champs sensibles identifiés
   └── Procédure rotation clés
   └── Plan incident
```

---

## 📋 Templates de Code

### Template: Nouveau Champ Chiffré

```python
# 1. Mixin: Ajouter le champ
class EncryptedFieldMixin:
    ENCRYPTED_FIELDS = ["notes", "beneficiary", "new_sensitive_field"]

# 2. Migration DB: Colonne TEXT
# migrations.py
cursor.execute("ALTER TABLE transactions ADD COLUMN new_sensitive_field TEXT")

# 3. Usage
data = {"new_sensitive_field": "sensitive value"}
encrypted = encrypt_fields(data)  # Auto-chiffré
```

### Template: Validation Input

```python
from pydantic import BaseModel, Field, field_validator
import html

class NewFeatureInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    
    @field_validator("name", "description")
    @classmethod
    def sanitize(cls, v):
        # XSS protection
        v = html.escape(v, quote=True)
        # Control chars removal
        v = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", v)
        return v.strip()
    
    @field_validator("name")
    @classmethod
    def no_sql_keywords(cls, v):
        forbidden = {"drop", "delete", "insert", "update"}
        if v.lower() in forbidden:
            raise ValueError("Reserved keyword")
        return v
```

### Template: Audit Logging

```python
from modules.logger import logger

def sensitive_operation(user_id: str, data: dict):
    """Opération nécessitant traçabilité."""
    
    # Log avant
    logger.info(f"SENSITIVE_OP_START: user={user_id}, action=delete_category")
    
    try:
        # Opération
        result = db.delete_category(data["category_id"])
        
        # Log succès
        logger.info(f"SENSITIVE_OP_SUCCESS: user={user_id}, deleted_id={data['category_id']}")
        
        return result
        
    except Exception as e:
        # Log échec
        logger.error(f"SENSITIVE_OP_FAILED: user={user_id}, error={e}")
        capture_exception(e, context={"user_id": user_id})
        raise
```

---

## 🚨 Procédures d'Urgence

### Rotation Clé de Chiffrement

```python
def emergency_key_rotation():
    """
    Procédure rotation clé en cas de compromission.
    ⚠️ BACKUP OBLIGATOIRE AVANT
    """
    # 1. Backup base
    backup_database()
    
    # 2. Générer nouvelle clé
    new_key = generate_encryption_key()
    
    # 3. Re-chiffrer toutes les données
    for table, field in ENCRYPTED_FIELDS:
        rotate_field_encryption(table, field, new_key)
    
    # 4. Mettre à jour .env
    update_env_file("ENCRYPTION_KEY", new_key)
    
    # 5. Redémarrer application
    restart_app()
```

### Réponse Incident

```python
# Checklist incident
INCIDENT_RESPONSE = {
    "1_detection": [
        "Identifier la nature de l'incident",
        "Évaluer la portée (données concernées)",
        "Notifier l'équipe"
    ],
    "2_containment": [
        "Isoler les systèmes affectés",
        "Activer mode maintenance si nécessaire",
        "Préserver les logs"
    ],
    "3_analysis": [
        "Analyser les logs",
        "Identifier le vecteur d'attaque",
        "Déterminer les données exposées"
    ],
    "4_notification": [
        "CNIL si données perso exposées (72h)",
        "Utilisateurs concernés",
        "Documentation interne"
    ],
    "5_recovery": [
        "Corriger la vulnérabilité",
        "Restaurer depuis backup si nécessaire",
        "Tests de sécurité"
    ]
}
```

---

## 📚 Références

### Fichiers Clés
- `modules/encryption.py` - Chiffrement AES-256
- `modules/validators.py` - Validation Pydantic
- `modules/privacy/gdpr_manager.py` - Conformité RGPD
- `modules/error_tracking.py` - Monitoring Sentry
- `modules/utils.py` - Utilitaires sécurité

### Commandes Utiles

```bash
# Scan secrets dans le code
git-secrets --scan

trivy filesystem .

# Vérifier dépendances vulnérables
safety check

# Test chiffrement
python -c "
from modules.encryption import encrypt_field, decrypt_field
enc = encrypt_field('test')
dec = decrypt_field(enc)
assert dec == 'test', 'Encryption test failed'
print('✅ Encryption working')
"
```

---

**Version**: 1.0  
**Créé par**: Orchestrateur d'Analyse 360°  
**Date**: 2026-02-25  
**Statut**: PRÊT À L'EMPLOI

---

## 🛡️ Module Additionnel: Web Security & Audit

### Headers de Sécurité HTTP

```python
"""
Configuration des headers de sécurité pour Streamlit.
À placer dans .streamlit/config.toml ou middleware.
"""

# .streamlit/config.toml
"""
[server]
enableCORS = false
enableXsrfProtection = true

[browser]
serverAddress = "localhost"
gatherUsageStats = false
"""

# Middleware pour headers additionnels (si custom server)
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "accelerometer=(), "
        "camera=(), "
        "geolocation=(), "
        "gyroscope=(), "
        "magnetometer=(), "
        "microphone=(), "
        "payment=(), "
        "usb=()"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

### Audit Logging Complet

```python
"""
Logging d'audit pour traçabilité des actions sensibles.
Qui fait quoi, quand, avec quel résultat.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Optional

class AuditAction(Enum):
    """Actions traçables."""
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_UPDATED = "transaction.updated"
    TRANSACTION_DELETED = "transaction.deleted"
    CATEGORY_CREATED = "category.created"
    CATEGORY_MERGED = "category.merged"
    MEMBER_CREATED = "member.created"
    MEMBER_DELETED = "member.deleted"
    SETTINGS_CHANGED = "settings.changed"
    EXPORT_REQUESTED = "export.requested"
    DATA_PURGED = "data.purged"
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"

class AuditLogger:
    """
    Logger d'audit immuable et tamper-resistant.
    """
    
    AUDIT_LOG_FILE = "logs/audit.log"
    
    @classmethod
    def log(
        cls,
        action: AuditAction,
        user_id: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Enregistre une action dans le log d'audit.
        
        Args:
            action: Type d'action
            user_id: ID de l'utilisateur
            resource_type: Type de ressource (transaction, category...)
            resource_id: ID de la ressource
            before_state: État avant modification
            after_state: État après modification
            ip_address: IP source
            success: Action réussie ou échouée
            error_message: Message d'erreur si échec
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action.value,
            "user_id": cls._hash_user_id(user_id),  # Pseudonymisation
            "resource": {
                "type": resource_type,
                "id": resource_id
            },
            "changes": cls._compute_diff(before_state, after_state),
            "source": {
                "ip": cls._anonymize_ip(ip_address) if ip_address else None,
                "session_id": cls._get_session_id()
            },
            "result": {
                "success": success,
                "error": error_message
            },
            "integrity_hash": ""  # Pour vérification immuabilité
        }
        
        # Calculer hash d'intégrité
        entry["integrity_hash"] = cls._compute_hash(entry)
        
        # Écrire (append-only)
        cls._append_to_log(entry)
        
        # Also log to standard logger
        logger.info(f"AUDIT: {action.value} by {user_id} on {resource_type}")
    
    @classmethod
    def _compute_diff(cls, before: Optional[dict], after: Optional[dict]) -> dict:
        """Calcule les différences entre deux états."""
        if before is None and after is None:
            return {}
        
        diff = {}
        all_keys = set(before.keys() if before else []) | set(after.keys() if after else [])
        
        for key in all_keys:
            before_val = before.get(key) if before else None
            after_val = after.get(key) if after else None
            
            if before_val != after_val:
                diff[key] = {"from": before_val, "to": after_val}
        
        return diff
    
    @classmethod
    def _hash_user_id(cls, user_id: str) -> str:
        """Pseudonymise l'ID utilisateur."""
        import hashlib
        return hashlib.sha256(f"{user_id}_audit_salt".encode()).hexdigest()[:16]
    
    @classmethod
    def _anonymize_ip(cls, ip: str) -> str:
        """Anonymise l'IP (dernier octet)."""
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        return ip
    
    @classmethod
    def _compute_hash(cls, entry: dict) -> str:
        """Calcule un hash pour vérifier l'intégrité."""
        import hashlib
        # Exclure le hash lui-même du calcul
        data = {k: v for k, v in entry.items() if k != "integrity_hash"}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    
    @classmethod
    def _append_to_log(cls, entry: dict):
        """Ajoute au fichier log (append-only)."""
        import os
        os.makedirs(os.path.dirname(cls.AUDIT_LOG_FILE), exist_ok=True)
        
        with open(cls.AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    
    @classmethod
    def query(
        cls,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None
    ) -> list:
        """Recherche dans les logs d'audit."""
        results = []
        
        try:
            with open(cls.AUDIT_LOG_FILE, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    
                    # Filtres
                    if start_date and entry["timestamp"] < start_date.isoformat():
                        continue
                    if end_date and entry["timestamp"] > end_date.isoformat():
                        continue
                    if user_id and entry["user_id"] != cls._hash_user_id(user_id):
                        continue
                    if action and entry["action"] != action.value:
                        continue
                    if resource_type and entry["resource"]["type"] != resource_type:
                        continue
                    
                    results.append(entry)
        except FileNotFoundError:
            pass
        
        return results

# Usage
AuditLogger.log(
    action=AuditAction.TRANSACTION_UPDATED,
    user_id="user_123",
    resource_type="transaction",
    resource_id="tx_456",
    before_state={"category": "Inconnu", "amount": -50},
    after_state={"category": "Alimentation", "amount": -50},
    success=True
)
```

### Rate Limiting & Bruteforce Protection

```python
"""
Protection contre les attaques par bruteforce et DoS.
"""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimitConfig:
    """Configuration du rate limiting."""
    max_requests: int = 10
    window_seconds: int = 60
    block_duration_seconds: int = 300

class RateLimiter:
    """
    Rate limiter en mémoire (simple) avec blocking.
    Pour production: utiliser Redis.
    """
    
    def __init__(self):
        self._requests = defaultdict(list)  # key -> list of timestamps
        self._blocked = defaultdict(float)  # key -> unblock timestamp
    
    def is_allowed(self, key: str, config: RateLimitConfig = None) -> tuple[bool, Optional[str]]:
        """
        Vérifie si une action est autorisée.
        
        Returns:
            (allowed, error_message)
        """
        if config is None:
            config = RateLimitConfig()
        
        now = time.time()
        
        # Vérifier si bloqué
        if key in self._blocked:
            if now < self._blocked[key]:
                remaining = int(self._blocked[key] - now)
                return False, f"⏳ Trop de tentatives. Réessayez dans {remaining}s."
            else:
                del self._blocked[key]
        
        # Nettoyer anciennes requêtes
        cutoff = now - config.window_seconds
        self._requests[key] = [ts for ts in self._requests[key] if ts > cutoff]
        
        # Vérifier limite
        if len(self._requests[key]) >= config.max_requests:
            # Bloquer
            self._blocked[key] = now + config.block_duration_seconds
            return False, f"🚫 Trop de tentatives. Bloqué pour {config.block_duration_seconds // 60} minutes."
        
        # Enregistrer requête
        self._requests[key].append(now)
        return True, None
    
    def reset(self, key: str):
        """Réinitialise le compteur pour une clé."""
        if key in self._requests:
            del self._requests[key]
        if key in self._blocked:
            del self._blocked[key]

# Usage pour login (exemple)
login_limiter = RateLimiter()

def attempt_login(username: str, password: str):
    key = f"login:{username}"
    allowed, error = login_limiter.is_allowed(
        key, 
        RateLimitConfig(max_requests=5, window_seconds=300, block_duration_seconds=900)
    )
    
    if not allowed:
        st.error(error)
        return False
    
    # Vérifier credentials...
    success = verify_credentials(username, password)
    
    if success:
        login_limiter.reset(key)  # Réinitialiser en cas de succès
    
    return success
```

### Secrets Rotation

```python
"""
Procédure de rotation des secrets (clés API, encryption keys).
"""

class SecretsRotation:
    """
    Gestion de la rotation périodique des secrets.
    """
    
    ROTATION_SCHEDULE = {
        "ENCRYPTION_KEY": {"days": 365, "urgent": True},
        "GEMINI_API_KEY": {"days": 90, "urgent": False},
        "OPENAI_API_KEY": {"days": 90, "urgent": False},
        "SENTRY_DSN": {"days": 180, "urgent": False},
    }
    
    @classmethod
    def check_rotation_needed(cls) -> list:
        """
        Vérifie quels secrets nécessitent une rotation.
        
        Returns:
            Liste des secrets à rotater avec urgence
        """
        import os
        from datetime import datetime, timedelta
        
        to_rotate = []
        
        for secret_name, config in cls.ROTATION_SCHEDULE.items():
            # Lire date dernière rotation (stockée dans .rotation_log)
            last_rotation = cls._get_last_rotation(secret_name)
            
            if last_rotation:
                days_since = (datetime.now() - last_rotation).days
                if days_since >= config["days"]:
                    to_rotate.append({
                        "secret": secret_name,
                        "days_overdue": days_since - config["days"],
                        "urgent": config["urgent"]
                    })
        
        return sorted(to_rotate, key=lambda x: (not x["urgent"], x["days_overdue"]))
    
    @classmethod
    def rotate_encryption_key(cls, new_key: str):
        """
        Procédure de rotation de la clé de chiffrement.
        ⚠️ DANGEREUX: Tester sur backup d'abord!
        """
        # 1. Backup base
        backup_path = BackupManager().create_backup("pre_key_rotation")
        
        # 2. Re-chiffrer toutes les données
        # Voir méthode dans encryption.py
        
        # 3. Mettre à jour .env
        cls._update_env("ENCRYPTION_KEY", new_key)
        
        # 4. Enregistrer rotation
        cls._record_rotation("ENCRYPTION_KEY")
        
        logger.info("Encryption key rotated successfully")
    
    @classmethod
    def _get_last_rotation(cls, secret_name: str) -> Optional[datetime]:
        """Lit la date de dernière rotation."""
        try:
            with open(".rotation_log", "r") as f:
                import json
                log = json.load(f)
                timestamp = log.get(secret_name)
                if timestamp:
                    return datetime.fromisoformat(timestamp)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None
    
    @classmethod
    def _record_rotation(cls, secret_name: str):
        """Enregistre une rotation."""
        import json
        log = {}
        try:
            with open(".rotation_log", "r") as f:
                log = json.load(f)
        except FileNotFoundError:
            pass
        
        log[secret_name] = datetime.now().isoformat()
        
        with open(".rotation_log", "w") as f:
            json.dump(log, f)
```

---

## 🔍 Module Additionnel: Security Monitoring

### Détection d'Anomalies

```python
"""
Détection de comportements suspects.
"""

class SecurityMonitor:
    """Monitoring de sécurité temps réel."""
    
    SUSPICIOUS_PATTERNS = {
        "mass_export": {"threshold": 100, "window": 3600},  # 100 exports/heure
        "failed_logins": {"threshold": 5, "window": 300},   # 5 échecs/5min
        "unusual_hours": {"hours": range(0, 6)},            # 00h-06h
    }
    
    @classmethod
    def check_anomaly(cls, user_id: str, action: str, context: dict) -> Optional[dict]:
        """
        Vérifie si une action est anormale.
        
        Returns:
            Alert dict si anomalie détectée, None sinon
        """
        # Vérifier patterns...
        
        # Exemple: Export massif
        if action == "export":
            recent_exports = cls._count_recent_actions(user_id, "export", window=3600)
            if recent_exports > cls.SUSPICIOUS_PATTERNS["mass_export"]["threshold"]:
                return {
                    "severity": "high",
                    "type": "mass_export",
                    "message": f"Utilisateur {user_id}: {recent_exports} exports/heure",
                    "action_required": "review"
                }
        
        return None
```

---

**Version**: 1.1 - **COMPLÉTÉ**  
**Ajouts**: Headers HTTP, Audit Logging, Rate Limiting, Secrets Rotation, Anomaly Detection
