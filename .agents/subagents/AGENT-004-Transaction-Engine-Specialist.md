# AGENT-004: Transaction Engine Specialist

## 🎯 Mission

Architecte du moteur de transactions de FinancePerso. Responsable de l'ingestion, la validation, la déduplication et le cycle de vie complet des transactions. Garant de l'intégrité des données financières importées.

---

## 📚 Contexte: Architecture Transaction Engine

### Philosophie
> "Une transaction est une promesse. Une fois importée, elle doit être traçable, vérifiable et immutable."

### Flux de Données

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRANSACTION LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CSV Import          Parsing          Validation          Storage   │
│  ┌────────┐         ┌────────┐        ┌──────────┐       ┌─────────┐│
│  │ Bourso │────────→│ Parse  │───────→│ Deduplic │──────→│  DB     ││
│  │ Generic│         │ Clean  │        │ Validate │       │ Pending ││
│  │ Other  │         │ Enrich │        │ Preview  │       │ Status  ││
│  └────────┘         └────────┘        └──────────┘       └─────────┘│
│       ↑                                                       │     │
│       │                                                       ↓     │
│  ┌────────┐                                            ┌─────────┐  │
│  │ Export │←───────────────────────────────────────────│Validated│  │
│  │  CSV   │                                            │  Done   │  │
│  └────────┘                                            └─────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Architecture Hash (Déduplication)

```python
"""
Système de hash pour déduplication robuste.
Inclus: date + label normalisé + montant + index d'occurrence
"""

def generate_tx_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère un hash unique par transaction.
    
    Algorithm:
    1. Normaliser le label (strip, uppercase)
    2. Calculer index d'occurrence local (pour transactions identiques même jour)
    3. SHA-256(date|label|amount|occurrence)[:16]
    
    Note: account_label EXCLU du hash pour éviter doublons si renommage compte.
    """
    df = df.sort_values(by=["date", "label", "amount"])
    df["_local_occ"] = df.groupby(["date", "label", "amount"]).cumcount()
    
    def calculate_hash(row):
        norm_label = str(row["label"]).strip().upper()
        base = f"{row['date']}|{norm_label}|{row['amount']}|{row['_local_occ']}"
        return hashlib.sha256(base.encode()).hexdigest()[:16]
    
    df["tx_hash"] = df.apply(calculate_hash, axis=1)
    return df.drop(columns=["_local_occ"])
```

---

## 📥 Module 1: Import & Parsing

### Parsers Supportés

| Format | Parser | Spécificités |
|--------|--------|--------------|
| **BoursoBank** | `parse_bourso_csv()` | Séparateur `;`, encoding UTF-8, décimal `,` |
| **Générique** | `parse_generic_csv()` | Configurable (séparateur, colonnes, formats) |
| **Automatique** | `detect_and_parse()` | Détection auto format basée sur headers |

### Parser BoursoBank

```python
def parse_bourso_csv(file) -> pd.DataFrame:
    """
    Parse le format spécifique BoursoBank.
    
    Mapping colonnes:
    - dateOp → date
    - label → label (+ extraction card_suffix via regex CB\*(\d{4}))
    - amount → amount (conversion virgule → point)
    - category → original_category
    - accountNum → account_id
    - accountLabel → account_label
    
    Enrichissement:
    - card_suffix: 4 derniers digits carte
    - member: "Carte {suffix}" ou "Inconnu"
    - status: "pending"
    - category_validated: "Inconnu"
    
    Returns:
        DataFrame avec tx_hash
    """
    df = pd.read_csv(file, sep=";", encoding="utf-8", decimal=",", thousands=" ")
    
    # Mapping et enrichissement...
    
    return generate_tx_hash(df)
```

### Parser Générique Configurable

```python
def parse_generic_csv(file, config: dict) -> pd.DataFrame:
    """
    Parse CSV avec configuration dynamique.
    
    Args:
        config: {
            "delimiter": ";",
            "encoding": "utf-8",
            "decimal": ",",
            "date_format": "%Y-%m-%d",
            "columns": {
                "date": "date_col_name",
                "label": "label_col_name",
                "amount": "amount_col_name"
            }
        }
    """
    df = pd.read_csv(
        file,
        sep=config.get("delimiter", ","),
        encoding=config.get("encoding", "utf-8"),
        decimal=config.get("decimal", ".")
    )
    
    # Renommage colonnes
    column_map = config["columns"]
    df = df.rename(columns={v: k for k, v in column_map.items()})
    
    # Conversion types
    df["date"] = pd.to_datetime(df["date"], format=config["date_format"]).dt.date
    df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(" ", ""))
    
    return generate_tx_hash(df)
```

### Détection Automatique Format

```python
class CSVFormatDetector:
    """Détecte automatiquement le format d'un CSV bancaire."""
    
    KNOWN_FORMATS = {
        "boursobank": {
            "required_columns": ["dateOp", "label", "amount"],
            "delimiter": ";",
            "sample_row": {"dateOp": "2026-01-15", "label": "CB*1234 AMAZON"}
        },
        "lcl": {
            "required_columns": ["Date", "Libelle", "Montant"],
            "delimiter": ";"
        },
        "sg": {
            "required_columns": ["Date", "Libellé", "Montant(EUROS)"],
            "delimiter": ";"
        }
    }
    
    @classmethod
    def detect(cls, file) -> tuple[str, dict]:
        """
        Détecte le format et retourne la config.
        
        Returns:
            (format_name, config_dict)
        """
        # Tester différents encodings et délimiteurs
        for encoding in ["utf-8", "latin1", "cp1252"]:
            for delimiter in [";", ",", "\t"]:
                try:
                    df = pd.read_csv(file, nrows=5, encoding=encoding, delimiter=delimiter)
                    
                    for format_name, format_config in cls.KNOWN_FORMATS.items():
                        if all(col in df.columns for col in format_config["required_columns"]):
                            return format_name, {
                                "delimiter": delimiter,
                                "encoding": encoding,
                                "columns": format_config["required_columns"]
                            }
                except Exception:
                    continue
        
        return "unknown", {}
```

---

## 🔄 Module 2: Deduplication Strategy

### Count-Based Verification

```python
"""
Stratégie de déduplication par comptage.
Gère les imports partiels et les doublons intelligemment.
"""

def save_transactions(df: pd.DataFrame) -> tuple[int, int]:
    """
    Sauvegarde avec vérification par comptage.
    
    Algorithm:
    1. Grouper input par (date, label, amount)
    2. Batch query: Compter existants en DB pour tous les groupes
    3. Insérer uniquement le surplus (input_count - db_count)
    
    Args:
        df: DataFrame à importer
        
    Returns:
        (new_count, skipped_count)
        
    Example:
        - Input: 5x "Courses Carrefour -50€ 2026-02-25"
        - DB: 3x existants
        - Import: 2 nouveaux, 3 ignorés
    """
    # Group by signature
    grouped = df.groupby(["date_str", "label", "amount"])
    
    # Batch count query
    unique_sigs = [(date, label, amount) for (date, label, amount), _ in grouped]
    placeholders = ",".join(["(?,?,?)"] * len(unique_sigs))
    
    cursor.execute(f"""
        SELECT date, label, amount, COUNT(*) as cnt
        FROM transactions
        WHERE (date, label, amount) IN ({placeholders})
        GROUP BY date, label, amount
    """, [item for sig in unique_sigs for item in sig])
    
    db_counts = {(row[0], row[1], row[2]): row[3] for row in cursor.fetchall()}
    
    # Insert surplus only
    for (date, label, amount), group in grouped:
        db_count = db_counts.get((date, label, amount), 0)
        input_count = len(group)
        to_insert = max(0, input_count - db_count)
        
        if to_insert > 0:
            rows_to_insert.extend(group.tail(to_insert).to_dict("records"))
    
    # Batch insert
    cursor.executemany("INSERT INTO transactions ...", rows_to_insert)
```

### Preview d'Import

```python
def preview_import(file, parser_config: dict) -> dict:
    """
    Génère un aperçu avant import final.
    
    Returns:
        {
            "total_rows": 150,
            "new_rows": 120,
            "duplicate_rows": 30,
            "sample_new": [...],
            "sample_duplicates": [...],
            "date_range": {"min": "2026-01-01", "max": "2026-02-25"},
            "amount_stats": {"total": -5000, "avg": -33.33}
        }
    """
    df = parse_csv(file, parser_config)
    
    # Compter existants
    existing_hashes = get_all_hashes()
    df["is_duplicate"] = df["tx_hash"].isin(existing_hashes)
    
    new_df = df[~df["is_duplicate"]]
    dup_df = df[df["is_duplicate"]]
    
    return {
        "total_rows": len(df),
        "new_rows": len(new_df),
        "duplicate_rows": len(dup_df),
        "sample_new": new_df.head(5).to_dict("records"),
        "sample_duplicates": dup_df.head(3).to_dict("records"),
        "date_range": {
            "min": df["date"].min(),
            "max": df["date"].max()
        },
        "amount_stats": {
            "total": df["amount"].sum(),
            "avg": df["amount"].mean()
        }
    }
```

---

## ✏️ Module 3: Validation & Enrichissement

### Validation Pipeline

```python
class TransactionValidator:
    """Pipeline de validation des transactions."""
    
    VALIDATION_RULES = [
        "required_fields",
        "date_format",
        "amount_range",
        "label_not_empty",
        "no_future_date"
    ]
    
    @classmethod
    def validate(cls, transaction: dict) -> tuple[bool, list[str]]:
        """
        Valide une transaction.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required = ["date", "label", "amount", "tx_hash"]
        for field in required:
            if not transaction.get(field):
                errors.append(f"Champ requis manquant: {field}")
        
        # Date validation
        try:
            date = pd.to_datetime(transaction["date"])
            if date > pd.Timestamp.now() + pd.Timedelta(days=1):
                errors.append("Date dans le futur")
            if date < pd.Timestamp("2000-01-01"):
                errors.append("Date trop ancienne")
        except Exception:
            errors.append("Format de date invalide")
        
        # Amount validation
        try:
            amount = float(transaction["amount"])
            if abs(amount) > 1_000_000:
                errors.append("Montant anormal (> 1M)")
        except Exception:
            errors.append("Montant invalide")
        
        # Label validation
        label = str(transaction.get("label", "")).strip()
        if len(label) < 2:
            errors.append("Libellé trop court")
        if len(label) > 500:
            errors.append("Libellé trop long (> 500 caractères)")
        
        return len(errors) == 0, errors
```

### Enrichissement Automatique

```python
def enrich_transaction(tx: dict) -> dict:
    """
    Enrichit une transaction avec des métadonnées.
    
    Enrichissements:
    - card_suffix: Extrait du libellé (CB*XXXX)
    - member: Détecté via card_suffix mappings
    - original_category: Nettoyée
    - quarter: Trimestre pour analyses
    - week: Numéro semaine
    """
    # Extraction carte
    match = re.search(r"CB\*(\d{4})", tx["label"], re.IGNORECASE)
    tx["card_suffix"] = match.group(1) if match else None
    
    # Détection membre
    if tx["card_suffix"]:
        mappings = get_member_mappings()
        tx["member"] = mappings.get(tx["card_suffix"], f"Carte {tx['card_suffix']}")
    else:
        tx["member"] = detect_member_from_content(tx["label"], None, tx.get("account_label"))
    
    # Annotations temporelles
    date = pd.to_datetime(tx["date"])
    tx["year"] = date.year
    tx["month"] = date.month
    tx["quarter"] = (date.month - 1) // 3 + 1
    tx["week"] = date.isocalendar()[1]
    tx["day_of_week"] = date.dayofweek
    
    return tx
```

---

## 📊 Module 4: Gestion Batch & Undo

### Transactions Batch

```python
def bulk_update_transactions(
    tx_ids: list[int],
    new_category: str,
    tags: str = None,
    beneficiary: str = None,
    notes: str = None
) -> str:
    """
    Met à jour plusieurs transactions avec undo support.
    
    Args:
        tx_ids: Liste des IDs à modifier
        new_category: Nouvelle catégorie
        tags: Tags (optionnel)
        beneficiary: Bénéficiaire (optionnel)
        notes: Notes (optionnel)
        
    Returns:
        action_id: ID du groupe d'action (pour undo)
    """
    action_id = str(uuid.uuid4())[:8]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Sauvegarder état avant
        cursor.execute(f"""
            INSERT INTO transaction_history 
            (action_group_id, tx_ids, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary, prev_notes)
            SELECT ?, id, status, category_validated, member, tags, beneficiary, notes
            FROM transactions WHERE id IN ({placeholders})
        """, [action_id] + tx_ids)
        
        # 2. Appliquer changements
        cursor.execute(f"""
            UPDATE transactions 
            SET category_validated = ?, status = 'validated', tags = ?, beneficiary = ?, notes = ?
            WHERE id IN ({placeholders})
        """, [new_category, tags, beneficiary, notes] + tx_ids)
        
        conn.commit()
    
    # Invalider cache
    get_all_transactions.clear()
    
    return action_id
```

### Undo System

```python
def undo_last_action() -> tuple[bool, str]:
    """
    Annule la dernière action batch.
    
    Returns:
        (success, message)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Récupérer dernière action
        cursor.execute("""
            SELECT action_group_id 
            FROM transaction_history 
            ORDER BY id DESC LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            return False, "Aucune action à annuler"
        
        action_id = row[0]
        
        # Récupérer tous les enregistrements de cette action
        cursor.execute("""
            SELECT tx_ids, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary, prev_notes
            FROM transaction_history
            WHERE action_group_id = ?
        """, (action_id,))
        
        entries = cursor.fetchall()
        
        # Restaurer état précédent
        for entry in entries:
            tx_id, prev_status, prev_category, prev_member, prev_tags, prev_beneficiary, prev_notes = entry
            
            cursor.execute("""
                UPDATE transactions 
                SET status = ?, category_validated = ?, member = ?, tags = ?, beneficiary = ?, notes = ?
                WHERE id = ?
            """, (prev_status, prev_category, prev_member, prev_tags, prev_beneficiary, prev_notes, tx_id))
        
        # Supprimer l'historique de cette action
        cursor.execute("DELETE FROM transaction_history WHERE action_group_id = ?", (action_id,))
        
        conn.commit()
    
    get_all_transactions.clear()
    
    return True, f"Action {action_id} annulée ({len(entries)} transactions restaurées)"
```

---

## 🔧 Responsabilités

### Quand consulter cet agent

✅ **OBLIGATOIRE**:
- Nouveau format de banque à supporter
- Modification de la logique de déduplication
- Changement dans le pipeline d'enrichissement
- Problème d'import CSV
- Modification du système d'undo
- Validation des transactions

❌ **PAS NÉCESSAIRE**:
- UI d'import (aller vers UI Agent)
- Catégorisation IA (aller vers Categorization Agent)
- Analytics/visualisations (aller vers Analytics Agent)

---

## 📋 Templates

### Template: Nouveau Parser

```python
def parse_newbank_csv(file) -> pd.DataFrame:
    """
    Parse format NewBank.
    
    Spécifications:
    - Séparateur: \t (tab)
    - Encoding: UTF-8 BOM
    - Date: DD/MM/YYYY
    - Montant: Colonne unique (négatif pour débit)
    """
    try:
        df = pd.read_csv(file, sep="\t", encoding="utf-8-sig")
        
        df = df.rename(columns={
            "Date operation": "date",
            "Libelle": "label",
            "Montant": "amount"
        })
        
        # Conversion date
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y").dt.date
        
        # Montant déjà au bon format
        df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(" ", ""))
        
        # Valeurs par défaut
        df["status"] = "pending"
        df["category_validated"] = "Inconnu"
        df["account_label"] = "NewBank"
        
        return generate_tx_hash(df)
        
    except Exception as e:
        logger.error(f"Error parsing NewBank CSV: {e}")
        raise
```

---

**Version**: 1.0
**Créé par**: Orchestrateur d'Analyse 360°
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI

---

## 🔧 Module Additionnel: Robustesse & Gestion d'Erreurs

### Validation Fichier

```python
"""
Validation pre-import des fichiers.
"""

import magic
from pathlib import Path

class FileValidator:
    """Validateur de fichiers d'import."""
    
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {'.csv', '.txt', '.tsv'}
    ALLOWED_MIME_TYPES = {
        'text/csv',
        'text/plain',
        'application/csv',
        'text/tab-separated-values'
    }
    
    @classmethod
    def validate(cls, file) -> tuple[bool, list[str]]:
        """
        Valide un fichier avant parsing.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Taille
        file.seek(0, 2)  # Fin
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)  # Reset
        
        if size_mb > cls.MAX_FILE_SIZE_MB:
            errors.append(f"Fichier trop volumineux ({size_mb:.1f}MB > {cls.MAX_FILE_SIZE_MB}MB)")
        
        # 2. Extension
        ext = Path(file.name).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            errors.append(f"Extension non supportee: {ext}")
        
        # 3. Type MIME
        mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)
        
        if mime not in cls.ALLOWED_MIME_TYPES:
            errors.append(f"Type fichier invalide: {mime}")
        
        # 4. Structure minimale
        try:
            sample = file.read(1024).decode('utf-8')
            file.seek(0)
            
            if not sample or len(sample.split('\n')) < 2:
                errors.append("Fichier vide ou trop petit")
            
            if ';' not in sample and ',' not in sample and '\t' not in sample:
                errors.append("Separateur non detecte (doit etre ; , ou tab)")
                
        except UnicodeDecodeError:
            errors.append("Encodage non UTF-8")
        
        return len(errors) == 0, errors
```

### Import Partiel (Lignes Valides/Invalides)

```python
"""
Import tolerant: accepte les lignes valides, rejette les invalides.
"""

@dataclass
class ImportResult:
    """Resultat d'import avec details."""
    success: bool
    imported_count: int
    rejected_count: int
    rejected_rows: list[dict]
    errors: list[str]
    warnings: list[str]

def import_with_tolerance(
    file,
    parser_config: dict,
    skip_invalid_rows: bool = True
) -> ImportResult:
    """
    Import avec tolerance aux erreurs.
    
    Args:
        file: Fichier CSV
        parser_config: Configuration parsing
        skip_invalid_rows: Si True, ignore les lignes invalides
        
    Returns:
        ImportResult avec details
    """
    # Lire tout le fichier
    try:
        df = pd.read_csv(
            file,
            sep=parser_config.get('delimiter', ';'),
            encoding=parser_config.get('encoding', 'utf-8'),
            decimal=parser_config.get('decimal', ',')
        )
    except Exception as e:
        return ImportResult(
            success=False,
            imported_count=0,
            rejected_count=0,
            rejected_rows=[],
            errors=[f"Erreur lecture fichier: {e}"],
            warnings=[]
        )
    
    valid_rows = []
    rejected_rows = []
    errors = []
    warnings = []
    
    for idx, row in df.iterrows():
        try:
            # Validation ligne par ligne
            validated = validate_row(row, parser_config)
            valid_rows.append(validated)
        except Exception as e:
            if skip_invalid_rows:
                rejected_rows.append({
                    'row_number': idx + 2,  # +2 pour header et 0-index
                    'data': row.to_dict(),
                    'error': str(e)
                })
                warnings.append(f"Ligne {idx + 2} ignoree: {e}")
            else:
                errors.append(f"Ligne {idx + 2} invalide: {e}")
    
    if errors and not skip_invalid_rows:
        return ImportResult(
            success=False,
            imported_count=0,
            rejected_count=len(rejected_rows),
            rejected_rows=rejected_rows,
            errors=errors,
            warnings=warnings
        )
    
    # Import des lignes valides
    if valid_rows:
        valid_df = pd.DataFrame(valid_rows)
        new_count, skipped = save_transactions(valid_df)
    else:
        new_count = 0
    
    return ImportResult(
        success=True,
        imported_count=new_count,
        rejected_count=len(rejected_rows),
        rejected_rows=rejected_rows,
        errors=[],
        warnings=warnings
    )
```

### Progress Tracking

```python
"""
Tracking de progression pour imports longs.
"""

import streamlit as st
from typing import Callable

class ImportProgressTracker:
    """Tracker de progression d'import."""
    
    def __init__(self, total_rows: int):
        self.total = total_rows
        self.processed = 0
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
    
    def update(self, increment: int = 1, message: str = None):
        """Met a jour la progression."""
        self.processed += increment
        progress = min(self.processed / self.total, 1.0)
        
        self.progress_bar.progress(progress)
        
        if message:
            self.status_text.text(f"{message} ({self.processed}/{self.total})")
        else:
            self.status_text.text(f"Traitement... {self.processed}/{self.total} lignes")
    
    def complete(self, message: str = "Import termine!"):
        """Marque comme complete."""
        self.progress_bar.progress(1.0)
        self.status_text.success(message)
    
    def error(self, message: str):
        """Marque comme erreur."""
        self.status_text.error(message)

# Usage
def import_large_file(file):
    df = pd.read_csv(file)
    tracker = ImportProgressTracker(len(df))
    
    for idx, row in df.iterrows():
        process_row(row)
        tracker.update(1, f"Traitement ligne {idx + 1}")
    
    tracker.complete(f"{len(df)} lignes traitees")
```

### Retry Mechanism

```python
"""
Retry pour operations d'import.
"""

from functools import wraps
import time

def with_import_retry(max_retries=3, delay=1.0):
    """Decorateur de retry pour imports."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, ConnectionError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                        logger.warning(f"Import retry {attempt + 1}/{max_retries}")
            
            raise last_error
        return wrapper
    return decorator

@with_import_retry(max_retries=3)
def save_transactions_robust(df: pd.DataFrame):
    """Version robuste avec retry."""
    return save_transactions(df)
```

---

**Version**: 1.1 - **COMPLETED**
**Ajouts**: Validation fichier, import partiel, progress tracking, retry mechanism
