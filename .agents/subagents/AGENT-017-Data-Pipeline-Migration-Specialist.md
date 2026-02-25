# AGENT-017: Data Pipeline & Migration Specialist

> **Spécialiste ETL et Migration de Données**  
> Responsable des pipelines d'import, migrations historiques, et transformations de format

---

## 🎯 Mission

Cet agent conçoit et implémente les pipelines ETL (Extract, Transform, Load) pour FinancePerso. Il gère l'import de données historiques, la migration depuis des outils concurrents, et assure l'intégrité des données tout au long du processus.

### Domaines d'expertise
- **ETL Pipelines** : Extraction, transformation, chargement de données massives
- **Migration historique** : Import multi-années avec conservation des relations
- **Format transformation** : Conversion entre formats bancaires (CSV, QIF, OFX, JSON)
- **Data Quality** : Profilage, cleansing, déduplication, validation
- **Reconciliation** : Vérification source vs cible, rapports d'erreurs

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE ORCHESTRATOR                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   EXTRACT    │→ │  TRANSFORM   │→ │    LOAD      │          │
│  │              │  │              │  │              │          │
│  │ • CSV Parser │  │ • Normalize  │  │ • Validate   │          │
│  │ • QIF Parser │  │ • Categorize │  │ • Insert     │          │
│  │ • OFX Parser │  │ • Deduplicate│  │ • Index      │          │
│  │ • JSON Parser│  │ • Enrich     │  │ • Cache      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              HISTORICAL MIGRATION ENGINE                         │
├─────────────────────────────────────────────────────────────────┤
│  Chunking │ Checkpointing │ Progress Tracking │ Rollback         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Module 1: ETL Core Architecture

### DataPipelineOrchestrator

```python
# modules/etl/pipeline_orchestrator.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Callable, List, Dict, Any, Optional
from enum import Enum, auto
import logging
import hashlib
import json
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    EXTRACT = auto()
    TRANSFORM = auto()
    VALIDATE = auto()
    LOAD = auto()
    COMMIT = auto()


@dataclass
class PipelineConfig:
    """Configuration d'un pipeline ETL."""
    chunk_size: int = 1000
    max_errors: int = 100
    dry_run: bool = False
    skip_validation: bool = False
    progress_callback: Optional[Callable[[int, int], None]] = None
    error_callback: Optional[Callable[[dict], None]] = None


@dataclass
class PipelineMetrics:
    """Métriques d'exécution du pipeline."""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    records_failed: int = 0
    errors: List[Dict] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    @property
    def success_rate(self) -> float:
        total = self.records_loaded + self.records_failed
        if total == 0:
            return 0.0
        return (self.records_loaded / total) * 100


@dataclass
class PipelineResult:
    """Résultat d'exécution d'un pipeline."""
    success: bool
    metrics: PipelineMetrics
    warnings: List[str] = field(default_factory=list)
    output_path: Optional[str] = None


class DataSource(ABC):
    """Source de données abstraite."""
    
    @abstractmethod
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extrait les données en streaming."""
        pass
    
    @abstractmethod
    def get_total_count(self) -> int:
        """Retourne le nombre total de records (estimation ok)."""
        pass
    
    @abstractmethod
    def validate_source(self) -> List[str]:
        """Valide la source avant extraction."""
        pass


class DataDestination(ABC):
    """Destination de données abstraite."""
    
    @abstractmethod
    def prepare(self) -> None:
        """Prépare la destination (création tables, indexes)."""
        pass
    
    @abstractmethod
    def load_batch(self, records: List[Dict]) -> int:
        """Charge un batch de records. Retourne nombre inséré."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Valide les changements."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Annule les changements."""
        pass


class DataTransformer(ABC):
    """Transformateur de données abstrait."""
    
    @abstractmethod
    def transform(self, record: Dict) -> Optional[Dict]:
        """Transforme un record. Retourne None pour filtrer."""
        pass


class DataPipelineOrchestrator:
    """
    Orchestrateur de pipelines ETL.
    
    Responsabilités:
    - Coordonner extraction → transformation → chargement
    - Gérer le chunking pour mémoire constante
    - Collecter métriques et erreurs
    - Support dry-run et validation
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.metrics = PipelineMetrics()
        self._transformers: List[DataTransformer] = []
        self._validators: List[Callable[[Dict], tuple[bool, str]]] = []
    
    def add_transformer(self, transformer: DataTransformer) -> 'DataPipelineOrchestrator':
        """Ajoute un transformateur (chaînables)."""
        self._transformers.append(transformer)
        return self
    
    def add_validator(self, validator: Callable[[Dict], tuple[bool, str]]) -> 'DataPipelineOrchestrator':
        """Ajoute un validateur."""
        self._validators.append(validator)
        return self
    
    def execute(
        self,
        source: DataSource,
        destination: DataDestination
    ) -> PipelineResult:
        """
        Exécute le pipeline complet.
        
        Args:
            source: Source de données
            destination: Destination des données
            
        Returns:
            PipelineResult avec métriques et statut
        """
        logger.info(f"Starting pipeline: {source.__class__.__name__} → {destination.__class__.__name__}")
        
        # Validation source
        source_errors = source.validate_source()
        if source_errors:
            return PipelineResult(
                success=False,
                metrics=self.metrics,
                warnings=source_errors
            )
        
        # Préparation destination
        destination.prepare()
        
        batch = []
        total_estimate = source.get_total_count()
        
        try:
            for record in source.extract():
                self.metrics.records_extracted += 1
                
                # Transformation
                transformed = self._apply_transformers(record)
                if transformed is None:
                    continue
                
                self.metrics.records_transformed += 1
                
                # Validation
                if not self.config.skip_validation:
                    is_valid, error = self._apply_validators(transformed)
                    if not is_valid:
                        self._handle_error(record, error)
                        continue
                
                batch.append(transformed)
                
                # Flush batch
                if len(batch) >= self.config.chunk_size:
                    self._flush_batch(destination, batch)
                    batch = []
                
                # Progress callback
                if self.config.progress_callback:
                    self.config.progress_callback(
                        self.metrics.records_extracted,
                        total_estimate
                    )
                
                # Vérifier limite erreurs
                if self.metrics.records_failed >= self.config.max_errors:
                    raise PipelineError(f"Max errors ({self.config.max_errors}) exceeded")
            
            # Flush final batch
            if batch:
                self._flush_batch(destination, batch)
            
            # Commit ou rollback selon dry_run
            if self.config.dry_run:
                destination.rollback()
                logger.info("Dry run completed - changes rolled back")
            else:
                destination.commit()
                logger.info("Pipeline completed successfully")
            
            self.metrics.completed_at = datetime.now()
            
            return PipelineResult(
                success=True,
                metrics=self.metrics
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            destination.rollback()
            self.metrics.completed_at = datetime.now()
            
            return PipelineResult(
                success=False,
                metrics=self.metrics,
                warnings=[str(e)]
            )
    
    def _apply_transformers(self, record: Dict) -> Optional[Dict]:
        """Applique tous les transformateurs en chaîne."""
        result = record
        for transformer in self._transformers:
            result = transformer.transform(result)
            if result is None:
                return None
        return result
    
    def _apply_validators(self, record: Dict) -> tuple[bool, str]:
        """Applique tous les validateurs."""
        for validator in self._validators:
            is_valid, error = validator(record)
            if not is_valid:
                return False, error
        return True, ""
    
    def _flush_batch(self, destination: DataDestination, batch: List[Dict]):
        """Charge un batch en destination."""
        if not self.config.dry_run:
            inserted = destination.load_batch(batch)
            self.metrics.records_loaded += inserted
    
    def _handle_error(self, record: Dict, error: str):
        """Gère une erreur de validation."""
        self.metrics.records_failed += 1
        error_info = {
            'record_hash': hashlib.md5(str(record).encode()).hexdigest()[:8],
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.metrics.errors.append(error_info)
        
        if self.config.error_callback:
            self.config.error_callback(error_info)
        
        logger.warning(f"Validation error: {error}")


class PipelineError(Exception):
    """Erreur de pipeline."""
    pass


# Fonctions utilitaires

def create_pipeline(config: PipelineConfig = None) -> DataPipelineOrchestrator:
    """Factory pour créer un pipeline."""
    return DataPipelineOrchestrator(config)


def run_import_pipeline(
    source: DataSource,
    destination: DataDestination,
    **config_options
) -> PipelineResult:
    """Shortcut pour exécuter un pipeline d'import."""
    config = PipelineConfig(**config_options)
    pipeline = DataPipelineOrchestrator(config)
    return pipeline.execute(source, destination)


---

## 🧱 Module 2: Format Parsers

### Parsers de formats bancaires

```python
# modules/etl/parsers/__init__.py

from .csv_parser import CSVParser
from .qif_parser import QIFParser
from .ofx_parser import OFXParser
from .json_parser import JSONParser, JSONLinesParser
from .excel_parser import ExcelParser

__all__ = [
    'CSVParser', 'QIFParser', 'OFXParser',
    'JSONParser', 'JSONLinesParser', 'ExcelParser'
]


# modules/etl/parsers/csv_parser.py

import csv
import chardet
from typing import Iterator, Dict, List, Any
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


class CSVParser(DataSource):
    """
    Parser CSV avec auto-détection encodage et séparateur.
    
    Supporte:
    - Auto-détection encodage (UTF-8, Latin-1, CP1252)
    - Auto-détection séparateur (virgule, point-virgule, tab)
    - Détection format dates multiples
    - Détection séparateur décimal
    """
    
    COMMON_SEPARATORS = [',', ';', '\t', '|']
    COMMON_DATE_FORMATS = [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y',
        '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y'
    ]
    
    def __init__(
        self,
        file_path: str,
        encoding: str = None,  # Auto-detect if None
        delimiter: str = None,  # Auto-detect if None
        date_format: str = None,  # Auto-detect if None
        column_mapping: Dict[str, str] = None,
        skip_rows: int = 0,
        has_header: bool = True
    ):
        self.file_path = file_path
        self.encoding = encoding
        self.delimiter = delimiter
        self.date_format = date_format
        self.column_mapping = column_mapping or {}
        self.skip_rows = skip_rows
        self.has_header = has_header
        self._detected_config = {}
    
    def validate_source(self) -> List[str]:
        """Valide le fichier CSV."""
        errors = []
        
        try:
            with open(self.file_path, 'rb') as f:
                sample = f.read(4096)
        except FileNotFoundError:
            errors.append(f"File not found: {self.file_path}")
            return errors
        except PermissionError:
            errors.append(f"Permission denied: {self.file_path}")
            return errors
        
        if len(sample) == 0:
            errors.append("File is empty")
            return errors
        
        # Vérifier si binaire
        if b'\x00' in sample:
            errors.append("File appears to be binary, not CSV")
        
        return errors
    
    def get_total_count(self) -> int:
        """Estime le nombre de lignes."""
        try:
            with open(self.file_path, 'r', encoding=self._get_encoding()) as f:
                return sum(1 for _ in f) - self.skip_rows - (1 if self.has_header else 0)
        except:
            return 0
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extrait les données CSV."""
        encoding = self._get_encoding()
        delimiter = self._get_delimiter(encoding)
        
        with open(self.file_path, 'r', encoding=encoding, newline='') as f:
            # Skip rows
            for _ in range(self.skip_rows):
                next(f)
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Nettoyer les clés
                clean_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                
                # Appliquer mapping
                if self.column_mapping:
                    clean_row = self._apply_mapping(clean_row)
                
                # Parser les types
                parsed = self._parse_types(clean_row)
                
                yield parsed
    
    def _get_encoding(self) -> str:
        """Détecte l'encodage."""
        if self.encoding:
            return self.encoding
        
        with open(self.file_path, 'rb') as f:
            raw = f.read(10000)
            result = chardet.detect(raw)
            detected = result.get('encoding', 'utf-8')
            self._detected_config['encoding'] = detected
            return detected
    
    def _get_delimiter(self, encoding: str) -> str:
        """Détecte le séparateur."""
        if self.delimiter:
            return self.delimiter
        
        with open(self.file_path, 'r', encoding=encoding) as f:
            sample = f.read(4096)
        
        counts = {sep: sample.count(sep) for sep in self.COMMON_SEPARATORS}
        detected = max(counts, key=counts.get)
        
        if counts[detected] == 0:
            detected = ','  # Default
        
        self._detected_config['delimiter'] = detected
        return detected
    
    def _apply_mapping(self, row: Dict) -> Dict:
        """Applique le mapping de colonnes."""
        result = {}
        for old_key, new_key in self.column_mapping.items():
            if old_key in row:
                result[new_key] = row[old_key]
        # Conserver colonnes non mappées
        for key, value in row.items():
            if key not in self.column_mapping:
                result[key] = value
        return result
    
    def _parse_types(self, row: Dict) -> Dict:
        """Parse les types de données."""
        result = {}
        
        for key, value in row.items():
            # Date
            if any(d in key.lower() for d in ['date', 'jour', 'time']):
                parsed = self._parse_date(value)
                result[key] = parsed
            # Montant
            elif any(m in key.lower() for m in ['amount', 'montant', 'prix', 'solde']):
                parsed = self._parse_amount(value)
                result[key] = parsed
            else:
                result[key] = value
        
        return result
    
    def _parse_date(self, value: str) -> datetime:
        """Parse une date avec formats communs."""
        if not value:
            return None
        
        for fmt in self.COMMON_DATE_FORMATS:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        
        return value  # Retourner tel quel si échec
    
    def _parse_amount(self, value: str) -> Decimal:
        """Parse un montant."""
        if not value:
            return Decimal('0')
        
        # Nettoyer
        clean = value.replace(' ', '').replace('€', '').replace('$', '')
        
        # Détecter séparateur décimal
        if ',' in clean and '.' in clean:
            # Format US: 1,000.00
            if clean.rfind(',') < clean.rfind('.'):
                clean = clean.replace(',', '')
            else:
                # Format FR: 1.000,00
                clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            # Peut être séparateur décimal ou milliers
            parts = clean.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                clean = clean.replace(',', '.')
            else:
                clean = clean.replace(',', '')
        
        try:
            return Decimal(clean)
        except InvalidOperation:
            return Decimal('0')
    
    def get_detected_config(self) -> Dict:
        """Retourne la configuration détectée."""
        return self._detected_config.copy()


# modules/etl/parsers/qif_parser.py

import re
from typing import Iterator, Dict, List
from datetime import datetime
from decimal import Decimal


class QIFParser(DataSource):
    """
    Parser QIF (Quicken Interchange Format).
    Format legacy encore utilisé par certaines banques.
    """
    
    QIF_TYPES = {
        '!Type:Bank': 'bank',
        '!Type:Cash': 'cash',
        '!Type:CCard': 'credit_card',
        '!Type:Invst': 'investment'
    }
    
    def __init__(self, file_path: str, default_year: int = None):
        self.file_path = file_path
        self.default_year = default_year or datetime.now().year
    
    def validate_source(self) -> List[str]:
        errors = []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)
                if '!Type:' not in content:
                    errors.append("Not a valid QIF file (no !Type: header found)")
        except Exception as e:
            errors.append(f"Cannot read file: {e}")
        return errors
    
    def get_total_count(self) -> int:
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return content.count('^')
        except:
            return 0
    
    def extract(self) -> Iterator[Dict]:
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Séparer par type
        sections = re.split(r'(!Type:\w+)', content)
        
        current_type = 'unknown'
        
        for i, section in enumerate(sections):
            if section.startswith('!Type:'):
                current_type = self.QIF_TYPES.get(section.strip(), 'unknown')
                continue
            
            # Parser transactions dans cette section
            transactions = section.split('^')
            
            for trans in transactions:
                trans = trans.strip()
                if not trans:
                    continue
                
                parsed = self._parse_transaction(trans, current_type)
                if parsed:
                    yield parsed
    
    def _parse_transaction(self, trans: str, trans_type: str) -> Dict:
        """Parse une transaction QIF."""
        result = {'type': trans_type}
        
        lines = trans.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) < 2:
                continue
            
            code = line[0]
            value = line[1:].strip()
            
            if code == 'D':  # Date
                result['date'] = self._parse_qif_date(value)
            elif code == 'T':  # Amount
                result['amount'] = Decimal(value.replace(',', ''))
            elif code == 'P':  # Payee
                result['payee'] = value
            elif code == 'M':  # Memo
                result['memo'] = value
            elif code == 'C':  # Cleared status
                result['cleared'] = value
            elif code == 'N':  # Number/Check
                result['reference'] = value
            elif code == 'L':  # Category/Transfer
                result['category'] = value
        
        return result
    
    def _parse_qif_date(self, value: str) -> datetime:
        """Parse une date QIF (format varié)."""
        # Formats communs: "01/15/2024", "15/01/2024", "1/15'24"
        value = value.replace("'", "/")
        
        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y']:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        # Format QIF spécial: "15/ 1/24" (day/month/year)
        try:
            parts = value.replace(' ', '').split('/')
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000 if year < 50 else 1900
                return datetime(year, month, day)
        except:
            pass
        
        return None


# modules/etl/parsers/ofx_parser.py

import xml.etree.ElementTree as ET
from typing import Iterator, Dict, List
from datetime import datetime
from decimal import Decimal
import re


class OFXParser(DataSource):
    """
    Parser OFX (Open Financial Exchange).
    Format XML standard bancaire.
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def validate_source(self) -> List[str]:
        errors = []
        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(100)
                if b'OFXHEADER:' not in header and b'<OFX>' not in header:
                    errors.append("Not a valid OFX file")
        except Exception as e:
            errors.append(f"Cannot read file: {e}")
        return errors
    
    def get_total_count(self) -> int:
        try:
            tree = self._parse_ofx()
            return len(tree.findall('.//STMTTRN'))
        except:
            return 0
    
    def extract(self) -> Iterator[Dict]:
        tree = self._parse_ofx()
        
        for trans in tree.findall('.//STMTTRN'):
            yield self._parse_transaction(trans)
    
    def _parse_ofx(self) -> ET.Element:
        """Parse le fichier OFX (gère format SGML legacy)."""
        with open(self.file_path, 'rb') as f:
            content = f.read()
        
        # Extraire partie XML après headers
        if b'<OFX>' in content:
            xml_start = content.find(b'<OFX>')
            xml_content = content[xml_start:]
        else:
            xml_content = content
        
        # OFX SGML n'est pas toujours XML valide
        xml_str = xml_content.decode('utf-8', errors='ignore')
        
        # Convertir en XML
        xml_str = self._sgml_to_xml(xml_str)
        
        return ET.fromstring(xml_str)
    
    def _sgml_to_xml(self, sgml: str) -> str:
        """Convertit SGML OFX en XML valide."""
        lines = sgml.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('<?') or line.startswith('<!OFX'):
                continue
            
            # Tags avec contenu sur même ligne
            match = re.match(r'<(\w+)>([^<]*)', line)
            if match and not line.endswith('/>'):
                tag, content = match.groups()
                if content:
                    result.append(f"<{tag}>{content}</{tag}>")
                else:
                    result.append(f"<{tag}>")
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _parse_transaction(self, elem: ET.Element) -> Dict:
        """Parse un élément transaction."""
        result = {}
        
        mapping = {
            'TRNTYPE': 'type',
            'DTPOSTED': 'date_posted',
            'DTUSER': 'date_user',
            'TRNAMT': 'amount',
            'FITID': 'id',
            'NAME': 'name',
            'MEMO': 'memo',
            'CHECKNUM': 'check_number'
        }
        
        for ofx_tag, std_tag in mapping.items():
            child = elem.find(ofx_tag)
            if child is not None and child.text:
                value = child.text
                
                # Parser dates
                if 'date' in std_tag:
                    value = self._parse_ofx_date(value)
                # Parser montants
                elif std_tag == 'amount':
                    value = Decimal(value)
                
                result[std_tag] = value
        
        return result
    
    def _parse_ofx_date(self, value: str) -> datetime:
        """Parse une date OFX (format: 20240115120000)."""
        value = value.strip()
        
        try:
            if len(value) >= 14:
                return datetime.strptime(value[:14], '%Y%m%d%H%M%S')
            elif len(value) >= 8:
                return datetime.strptime(value[:8], '%Y%m%d')
        except ValueError:
            pass
        
        return None


---

## 🧱 Module 3: Historical Migration Engine

### Moteur de migration multi-années

```python
# modules/etl/migration_engine.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Checkpoint:
    """Point de reprise pour migration longue."""
    id: str
    timestamp: datetime
    records_processed: int
    last_record_id: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationPlan:
    """Plan de migration."""
    id: str
    name: str
    source_type: str  # 'bankin', 'linxo', 'csv', etc.
    year_from: int
    year_to: int
    priority_accounts: List[str] = field(default_factory=list)
    rules_override: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class MigrationResult:
    """Résultat d'une migration."""
    plan: MigrationPlan
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_imported: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    checkpoints: List[Checkpoint] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    @property
    def success_rate(self) -> float:
        total = self.records_imported + self.records_skipped + self.records_failed
        if total == 0:
            return 0.0
        return (self.records_imported / total) * 100


class HistoricalMigrationEngine:
    """
    Moteur de migration historique avec checkpointing.
    
    Capacités:
    - Migration par chunks (années/mois)
    - Points de reprise sur interruption
    - Rollback complet ou partiel
    - Validation incrémentale
    """
    
    def __init__(self, state_dir: str = "./migration_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._active_migrations: Dict[str, MigrationResult] = {}
    
    def create_migration_plan(
        self,
        name: str,
        source_type: str,
        year_from: int,
        year_to: int,
        **options
    ) -> MigrationPlan:
        """Crée un plan de migration."""
        plan = MigrationPlan(
            id=f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            source_type=source_type,
            year_from=year_from,
            year_to=year_to,
            **options
        )
        
        self._save_plan(plan)
        return plan
    
    def execute_migration(
        self,
        plan: MigrationPlan,
        data_source: DataSource,
        resume_from: str = None
    ) -> MigrationResult:
        """
        Exécute une migration avec support reprise.
        """
        result = MigrationResult(
            plan=plan,
            status=MigrationStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self._active_migrations[plan.id] = result
        
        try:
            if resume_from:
                checkpoint = self._load_checkpoint(resume_from)
                result.checkpoints.append(checkpoint)
                logger.info(f"Resuming from checkpoint: {resume_from}")
            
            # Stratégie par années
            for year in range(plan.year_from, plan.year_to + 1):
                if result.status == MigrationStatus.PAUSED:
                    break
                
                year_result = self._migrate_year(year, data_source, result)
                
                # Créer checkpoint après chaque année
                checkpoint = Checkpoint(
                    id=f"{plan.id}_year_{year}",
                    timestamp=datetime.now(),
                    records_processed=result.records_imported,
                    last_record_id=str(year),
                    context={'year': year, 'status': 'completed'}
                )
                result.checkpoints.append(checkpoint)
                self._save_checkpoint(checkpoint)
                
                # Accumuler résultats
                result.records_imported += year_result['imported']
                result.records_skipped += year_result['skipped']
                result.records_failed += year_result['failed']
                result.errors.extend(year_result.get('errors', []))
                result.warnings.extend(year_result.get('warnings', []))
            
            # Finaliser
            result.completed_at = datetime.now()
            result.status = MigrationStatus.COMPLETED if result.records_failed == 0 else MigrationStatus.FAILED
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            result.status = MigrationStatus.FAILED
            result.errors.append({
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'type': 'fatal'
            })
        
        finally:
            self._save_result(result)
            if plan.id in self._active_migrations:
                del self._active_migrations[plan.id]
        
        return result
    
    def _migrate_year(
        self,
        year: int,
        data_source: DataSource,
        result: MigrationResult
    ) -> Dict:
        """Migre une année spécifique."""
        logger.info(f"Migrating year {year}")
        
        year_stats = {'imported': 0, 'skipped': 0, 'failed': 0, 'errors': [], 'warnings': []}
        
        pipeline_config = PipelineConfig(
            chunk_size=500,
            max_errors=50,
            progress_callback=lambda current, total: logger.debug(
                f"Year {year}: {current}/{total}"
            )
        )
        
        orchestrator = DataPipelineOrchestrator(pipeline_config)
        orchestrator.add_transformer(DateRangeFilterTransformer(year))
        orchestrator.add_transformer(DuplicateDetectionTransformer())
        orchestrator.add_transformer(CategoryMappingTransformer(result.plan.rules_override.get('categories', {})))
        
        destination = FinancePersoDestination()
        pipeline_result = orchestrator.execute(data_source, destination)
        
        year_stats['imported'] = pipeline_result.metrics.records_loaded
        year_stats['failed'] = pipeline_result.metrics.records_failed
        year_stats['errors'] = pipeline_result.metrics.errors
        
        return year_stats
    
    def pause_migration(self, migration_id: str) -> bool:
        """Met en pause une migration active."""
        if migration_id in self._active_migrations:
            self._active_migrations[migration_id].status = MigrationStatus.PAUSED
            return True
        return False
    
    def rollback_migration(self, migration_id: str, to_checkpoint: str = None) -> bool:
        """Annule une migration."""
        result = self._load_result(migration_id)
        if not result:
            return False
        
        logger.warning(f"Rolling back migration {migration_id}")
        
        try:
            cutoff_date = result.started_at
            
            if to_checkpoint:
                checkpoint = next(
                    (c for c in result.checkpoints if c.id == to_checkpoint),
                    None
                )
                if checkpoint:
                    cutoff_date = checkpoint.timestamp
            
            self._soft_delete_transactions(result.plan.id, cutoff_date)
            
            result.status = MigrationStatus.ROLLED_BACK
            self._save_result(result)
            
            self._recalculate_aggregates()
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_status(self, migration_id: str) -> Optional[MigrationResult]:
        """Retourne le statut d'une migration."""
        if migration_id in self._active_migrations:
            return self._active_migrations[migration_id]
        return self._load_result(migration_id)
    
    def _save_plan(self, plan: MigrationPlan):
        """Sauvegarde un plan."""
        file_path = self.state_dir / f"plan_{plan.id}.json"
        with open(file_path, 'w') as f:
            json.dump(plan.__dict__, f, indent=2, default=str)
    
    def _save_checkpoint(self, checkpoint: Checkpoint):
        """Sauvegarde un checkpoint."""
        file_path = self.state_dir / f"checkpoint_{checkpoint.id}.json"
        with open(file_path, 'w') as f:
            json.dump(checkpoint.__dict__, f, indent=2, default=str)
    
    def _load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Charge un checkpoint."""
        file_path = self.state_dir / f"checkpoint_{checkpoint_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path) as f:
            data = json.load(f)
            return Checkpoint(**data)
    
    def _save_result(self, result: MigrationResult):
        """Sauvegarde un résultat."""
        file_path = self.state_dir / f"result_{result.plan.id}.json"
        with open(file_path, 'w') as f:
            json.dump(result.__dict__, f, indent=2, default=str)
    
    def _load_result(self, migration_id: str) -> Optional[MigrationResult]:
        """Charge un résultat."""
        file_path = self.state_dir / f"result_{migration_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path) as f:
            data = json.load(f)
            plan_data = data.pop('plan', {})
            plan = MigrationPlan(**plan_data)
            return MigrationResult(plan=plan, **data)
    
    def _soft_delete_transactions(self, migration_id: str, cutoff_date: datetime):
        """Marque transactions comme supprimées."""
        from modules.db.connection import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions
                SET deleted_at = ?, deleted_reason = ?
                WHERE created_at >= ? AND migration_id = ?
            """, (
                datetime.now(),
                f"rollback_migration_{migration_id}",
                cutoff_date,
                migration_id
            ))
            conn.commit()
            logger.info(f"Soft deleted {cursor.rowcount} transactions")
    
    def _recalculate_aggregates(self):
        """Recalcule les agrégats après rollback."""
        from modules.cache_manager import invalidate_all_caches
        from modules.budgets import recalculate_all_budgets
        
        invalidate_all_caches()
        recalculate_all_budgets()


# Transformateurs spécifiques migration

class DateRangeFilterTransformer(DataTransformer):
    """Filtre par plage de dates."""
    
    def __init__(self, year: int):
        self.year = year
        self.start = datetime(year, 1, 1)
        self.end = datetime(year, 12, 31, 23, 59, 59)
    
    def transform(self, record: Dict) -> Optional[Dict]:
        date = record.get('date')
        if not date:
            return record
        
        if isinstance(date, datetime):
            if self.start <= date <= self.end:
                return record
        
        return None


class DuplicateDetectionTransformer(DataTransformer):
    """Détecte et filtre les doublons basés sur hash."""
    
    def __init__(self):
        self._seen_hashes = set()
    
    def transform(self, record: Dict) -> Optional[Dict]:
        hash_input = f"{record.get('date')}|{record.get('amount')}|{record.get('description', '')}"
        record_hash = hashlib.md5(hash_input.encode()).hexdigest()
        
        if record_hash in self._seen_hashes:
            return None
        
        self._seen_hashes.add(record_hash)
        record['_hash'] = record_hash
        return record


class CategoryMappingTransformer(DataTransformer):
    """Mappe les catégories source vers catégories FinancePerso."""
    
    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping
    
    def transform(self, record: Dict) -> Optional[Dict]:
        source_category = record.get('category', '')
        
        if source_category in self.mapping:
            record['category'] = self.mapping[source_category]
            record['category_source'] = 'mapped'
        else:
            record['category_source'] = 'auto'
        
        return record


class FinancePersoDestination(DataDestination):
    """Destination vers base FinancePerso."""
    
    def __init__(self):
        self._buffer = []
        self._conn = None
    
    def prepare(self):
        from modules.db.connection import get_db_connection
        self._conn = get_db_connection()
    
    def load_batch(self, records: List[Dict]) -> int:
        if not self._conn:
            return 0
        
        cursor = self._conn.cursor()
        inserted = 0
        
        for record in records:
            try:
                cursor.execute("""
                    INSERT INTO transactions 
                    (date, amount, description, category, account, hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(hash) DO UPDATE SET
                        updated_at = ?
                    WHERE excluded.hash = transactions.hash
                """, (
                    record.get('date'),
                    float(record.get('amount', 0)),
                    record.get('description', ''),
                    record.get('category'),
                    record.get('account', 'default'),
                    record.get('_hash', ''),
                    datetime.now(),
                    datetime.now()
                ))
                inserted += 1
            except Exception as e:
                logger.warning(f"Insert failed: {e}")
        
        self._conn.commit()
        return inserted
    
    def commit(self):
        if self._conn:
            self._conn.commit()
    
    def rollback(self):
        if self._conn:
            self._conn.rollback()


---

## 🧱 Module 4: Data Quality Engine

### Validation et profiling des données

```python
# modules/etl/quality_engine.py

from dataclasses import dataclass
from typing import List, Dict, Any, Callable
from datetime import datetime
from decimal import Decimal
import json


@dataclass
class QualityReport:
    """Rapport de qualité des données."""
    total_records: int
    valid_records: int
    invalid_records: int
    issues: List[Dict]
    statistics: Dict[str, Any]
    
    @property
    def validity_score(self) -> float:
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100


class DataQualityEngine:
    """
    Moteur de qualité de données.
    
    Responsabilités:
    - Profiler les données sources
    - Détecter anomalies et outliers
    - Mesurer complétude et cohérence
    - Générer rapports de qualité
    """
    
    def __init__(self):
        self._rules: List[Callable[[Dict], tuple[bool, str]]] = []
    
    def add_rule(self, rule: Callable[[Dict], tuple[bool, str]]):
        """Ajoute une règle de validation."""
        self._rules.append(rule)
        return self
    
    def analyze(self, records: List[Dict]) -> QualityReport:
        """Analyse la qualité d'un jeu de données."""
        issues = []
        valid = 0
        invalid = 0
        
        stats = self._compute_statistics(records)
        
        for record in records:
            record_valid = True
            
            for rule in self._rules:
                is_valid, error = rule(record)
                if not is_valid:
                    record_valid = False
                    issues.append({
                        'record_index': records.index(record),
                        'error': error,
                        'field_values': self._extract_relevant_fields(record, error)
                    })
            
            if record_valid:
                valid += 1
            else:
                invalid += 1
        
        return QualityReport(
            total_records=len(records),
            valid_records=valid,
            invalid_records=invalid,
            issues=issues[:100],
            statistics=stats
        )
    
    def _compute_statistics(self, records: List[Dict]) -> Dict:
        """Calcule des statistiques sur les données."""
        stats = {
            'record_count': len(records),
            'fields_present': {},
            'date_range': {'min': None, 'max': None},
            'amount_range': {'min': None, 'max': None, 'sum': Decimal('0')},
            'categories': {}
        }
        
        for record in records:
            for field in record.keys():
                stats['fields_present'][field] = stats['fields_present'].get(field, 0) + 1
            
            date = record.get('date')
            if isinstance(date, datetime):
                if stats['date_range']['min'] is None or date < stats['date_range']['min']:
                    stats['date_range']['min'] = date
                if stats['date_range']['max'] is None or date > stats['date_range']['max']:
                    stats['date_range']['max'] = date
            
            amount = record.get('amount')
            if isinstance(amount, (int, float, Decimal)):
                stats['amount_range']['sum'] += Decimal(str(amount))
                current_min = stats['amount_range']['min']
                current_max = stats['amount_range']['max']
                
                if current_min is None or amount < current_min:
                    stats['amount_range']['min'] = amount
                if current_max is None or amount > current_max:
                    stats['amount_range']['max'] = amount
            
            category = record.get('category', 'uncategorized')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        return stats
    
    def _extract_relevant_fields(self, record: Dict, error: str) -> Dict:
        """Extrait les champs pertinents pour un rapport d'erreur."""
        relevant = {}
        for field in record.keys():
            if field.lower() in error.lower():
                relevant[field] = record[field]
        
        if not relevant:
            for key in ['date', 'amount', 'description', 'category']:
                if key in record:
                    relevant[key] = record[key]
        
        return relevant


# Règles de validation prédéfinies

class ValidationRules:
    """Collection de règles de validation réutilisables."""
    
    @staticmethod
    def required_field(field_name: str):
        """Vérifie qu'un champ est présent et non vide."""
        def validator(record: Dict) -> tuple[bool, str]:
            value = record.get(field_name)
            if value is None or value == '' or value == []:
                return False, f"Field '{field_name}' is required"
            return True, ""
        return validator
    
    @staticmethod
    def valid_date(field_name: str, min_date: datetime = None, max_date: datetime = None):
        """Vérifie qu'une date est valide."""
        def validator(record: Dict) -> tuple[bool, str]:
            value = record.get(field_name)
            if value is None:
                return True, ""
            
            if not isinstance(value, datetime):
                return False, f"Field '{field_name}' is not a valid date"
            
            if min_date and value < min_date:
                return False, f"Field '{field_name}' is before minimum date"
            
            if max_date and value > max_date:
                return False, f"Field '{field_name}' is after maximum date"
            
            return True, ""
        return validator
    
    @staticmethod
    def valid_amount(field_name: str, allow_zero: bool = True):
        """Vérifie qu'un montant est valide."""
        def validator(record: Dict) -> tuple[bool, str]:
            value = record.get(field_name)
            if value is None:
                return True, ""
            
            try:
                decimal_val = Decimal(str(value))
                if not allow_zero and decimal_val == 0:
                    return False, f"Field '{field_name}' cannot be zero"
                return True, ""
            except:
                return False, f"Field '{field_name}' is not a valid amount"
        return validator
    
    @staticmethod
    def valid_category(field_name: str, allowed_categories: List[str] = None):
        """Vérifie qu'une catégorie est valide."""
        def validator(record: Dict) -> tuple[bool, str]:
            value = record.get(field_name)
            if value is None or value == '':
                return True, ""
            
            if allowed_categories and value not in allowed_categories:
                return False, f"Field '{field_name}' has unknown category: {value}"
            
            return True, ""
        return validator


class ReconciliationEngine:
    """
    Moteur de réconciliation source vs cible.
    """
    
    def __init__(self):
        self.discrepancies = []
    
    def reconcile(
        self,
        source_records: List[Dict],
        target_records: List[Dict],
        key_fields: List[str] = None
    ) -> Dict:
        """
        Compare les données source et cible.
        """
        key_fields = key_fields or ['date', 'amount', 'description']
        
        source_index = {self._make_key(r, key_fields): r for r in source_records}
        target_index = {self._make_key(r, key_fields): r for r in target_records}
        
        source_keys = set(source_index.keys())
        target_keys = set(target_index.keys())
        
        missing_in_target = source_keys - target_keys
        extra_in_target = target_keys - source_keys
        common_keys = source_keys & target_keys
        
        modified = []
        for key in common_keys:
            source_rec = source_index[key]
            target_rec = target_index[key]
            
            differences = self._find_differences(source_rec, target_rec)
            if differences:
                modified.append({
                    'key': key,
                    'differences': differences
                })
        
        return {
            'source_count': len(source_records),
            'target_count': len(target_records),
            'missing_in_target': list(missing_in_target)[:100],
            'extra_in_target': list(extra_in_target)[:100],
            'modified': modified[:100],
            'match_rate': len(common_keys) / len(source_keys) * 100 if source_keys else 0
        }
    
    def _make_key(self, record: Dict, fields: List[str]) -> str:
        """Crée une clé unique."""
        values = [str(record.get(f, '')) for f in fields]
        return '|'.join(values)
    
    def _find_differences(self, source: Dict, target: Dict) -> List[Dict]:
        """Trouve les différences entre deux records."""
        differences = []
        all_fields = set(source.keys()) | set(target.keys())
        
        for field in all_fields:
            source_val = source.get(field)
            target_val = target.get(field)
            
            if source_val != target_val:
                differences.append({
                    'field': field,
                    'source': source_val,
                    'target': target_val
                })
        
        return differences


---

## 🧱 Module 5: Import UI Components

### Interface utilisateur pour imports

```python
# modules/etl/ui/import_wizard.py

import streamlit as st
from typing import Optional
import pandas as pd


def render_import_wizard():
    """
    Wizard d'import complet avec prévisualisation.
    """
    st.header("📥 Importer des transactions")
    
    # Étape 1: Upload fichier
    st.subheader("Étape 1: Sélectionner le fichier")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=['csv', 'qif', 'ofx', 'xlsx', 'json', 'jsonl'],
        help="Formats supportés: CSV, QIF, OFX, Excel, JSON"
    )
    
    if not uploaded_file:
        st.info("Veuillez sélectionner un fichier à importer")
        return
    
    # Sauvegarder temporairement
    temp_path = save_uploaded_file(uploaded_file)
    
    # Étape 2: Détection format
    st.subheader("Étape 2: Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        detected_format = detect_file_format(temp_path)
        st.write(f"**Format détecté:** {detected_format.upper()}")
        
        if detected_format == 'csv':
            render_csv_options(temp_path)
    
    with col2:
        st.write("**Mapping des colonnes**")
        mapping = render_column_mapping(temp_path, detected_format)
    
    # Étape 3: Prévisualisation
    st.subheader("Étape 3: Prévisualisation")
    
    if st.button("🔍 Analyser le fichier"):
        with st.spinner("Analyse en cours..."):
            preview = generate_preview(temp_path, detected_format, mapping)
            
            cols = st.columns(4)
            cols[0].metric("Total lignes", preview['total_rows'])
            cols[1].metric("Valides", preview['valid_rows'])
            cols[2].metric("Erreurs", preview['error_rows'])
            cols[3].metric("Doublons potentiels", preview['duplicates'])
            
            st.write("**Aperçu des 5 premières lignes:**")
            st.dataframe(preview['sample_df'], use_container_width=True)
            
            if preview['quality_report']:
                with st.expander("📊 Rapport de qualité"):
                    render_quality_report(preview['quality_report'])
    
    # Étape 4: Import
    st.subheader("Étape 4: Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dry_run = st.checkbox("Mode simulation (dry run)", value=True)
    
    with col2:
        skip_duplicates = st.checkbox("Ignorer les doublons", value=True)
        auto_categorize = st.checkbox("Catégoriser automatiquement", value=True)
    
    if st.button("🚀 Lancer l'import", type="primary", use_container_width=True):
        execute_import_with_progress(
            temp_path,
            detected_format,
            mapping,
            dry_run=dry_run,
            skip_duplicates=skip_duplicates,
            auto_categorize=auto_categorize
        )


def execute_import_with_progress(**kwargs):
    """Exécute l'import avec barre de progression."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_callback(current, total):
        progress = current / max(total, 1)
        progress_bar.progress(min(progress, 1.0))
        status_text.text(f"Import en cours... {current}/{total}")
    
    # Exécuter import...
    
    progress_bar.empty()
    status_text.empty()


# Fonctions utilitaires

def save_uploaded_file(uploaded_file) -> str:
    """Sauvegarde un fichier uploadé temporairement."""
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    return file_path


def detect_file_format(file_path: str) -> str:
    """Détecte le format d'un fichier."""
    ext = file_path.lower().split('.')[-1]
    format_mapping = {
        'csv': 'csv',
        'qif': 'qif',
        'ofx': 'ofx',
        'xlsx': 'excel',
        'xls': 'excel',
        'json': 'json',
        'jsonl': 'jsonl'
    }
    return format_mapping.get(ext, 'unknown')


---

## ✅ Checklists & Procédures

### Pré-import Checklist

```
AVANT TOUT IMPORT:
□ Backup base de données (export SQL complet)
□ Vérifier espace disque disponible (2x taille fichier estimée)
□ Identifier encodage fichier source
□ Valider format dates (échantillon)
□ Confirmer séparateur décimal (point ou virgule)
□ Vérifier intégrité fichier (pas de corruption)
□ Tester avec dry_run=True
□ Documenter mapping colonnes choisi

CONFIGURATION REQUISE:
□ Mapping 'date' → champ date
□ Mapping 'amount' → champ montant  
□ Mapping 'description' → champ description
□ (Optionnel) Mapping 'category' → catégorie
□ (Optionnel) Mapping 'account' → compte
□ Configurer règles de catégorisation
□ Définir stratégie doublons (hash-based ou champ unique)
```

### Migration Multi-années Checklist

```
PLANIFICATION:
□ Définir plage années (year_from, year_to)
□ Estimer volume par année
□ Identifier années problématiques (changements banque)
□ Préparer mapping catégories historiques
□ Créer plan de migration nommé

EXECUTION:
□ Lancer par tranches d'1 année
□ Vérifier checkpoint après chaque année
□ Valider comptage vs source
□ Contrôler sommes par année
□ Identifier erreurs récurrentes

POST-MIGRATION:
□ Vérifier total transactions importées
□ Contrôler date min/max en base
□ Vérifier sommes par compte
□ Recalculer budgets mensuels
□ Invalider tous les caches
□ Tester fonctionnalités clés (recherche, stats)
□ Générer rapport de réconciliation
□ Archiver fichiers sources
```

### Quality Gates

```python
# Niveaux de qualité acceptables

QUALITY_THRESHOLDS = {
    'csv_import': {
        'min_success_rate': 95.0,  # % réussite
        'max_duplicate_rate': 2.0,  # % doublons
        'max_missing_required': 0,   # champs requis manquants
        'max_date_outliers': 5.0    # % dates hors plage
    },
    'historical_migration': {
        'min_success_rate': 98.0,
        'max_duplicate_rate': 1.0,
        'year_balance_tolerance': 0.01  # 1 centime écart max
    },
    'bank_export': {
        'min_success_rate': 99.0,
        'required_fields': ['date', 'amount', 'description'],
        'max_future_dates': 0  # Pas de dates futures
    }
}
```

---

## 🚨 Procédures d'Urgence

### Migration Échouée à Mi-Chemin

```python
def handle_partial_migration_failure(migration_id: str):
    """
    Gestion d'échec partiel - Point de reprise.
    """
    engine = HistoricalMigrationEngine()
    result = engine.get_migration_status(migration_id)
    
    if not result:
        return {"error": "Migration not found"}
    
    last_checkpoint = result.checkpoints[-1] if result.checkpoints else None
    
    options = {
        "resume": {
            "label": "Reprendre depuis dernier checkpoint",
            "action": lambda: engine.execute_migration(
                result.plan,
                data_source=get_source_for_plan(result.plan),
                resume_from=last_checkpoint.id if last_checkpoint else None
            ),
            "available": last_checkpoint is not None
        },
        "rollback": {
            "label": "Annuler complètement (rollback)",
            "action": lambda: engine.rollback_migration(migration_id),
            "available": result.records_imported > 0
        }
    }
    
    return options
```

### Rollback Complet

```python
def emergency_rollback(migration_id: str, confirm: bool = False):
    """
    Procédure de rollback d'urgence.
    """
    if not confirm:
        return {
            "warning": "Cette action est irréversible",
            "impact": "Toutes les transactions de cette migration seront marquées supprimées"
        }
    
    engine = HistoricalMigrationEngine()
    result = engine.get_migration_status(migration_id)
    
    if not result:
        return {"error": "Migration not found"}
    
    logger.critical(f"EMERGENCY ROLLBACK initiated for migration {migration_id}")
    
    # 1. Arrêter migration si active
    engine.pause_migration(migration_id)
    
    # 2. Créer backup avant rollback
    backup_path = create_emergency_backup()
    
    # 3. Exécuter rollback
    success = engine.rollback_migration(migration_id)
    
    # 4. Vérifier intégrité post-rollback
    verification = verify_data_integrity()
    
    return {
        "success": success,
        "backup_path": backup_path,
        "verification": verification
    }
```

---

## 🏗️ Architecture Inter-Agent

```
AGENT-017 (Data Pipeline)
         │
         ├──→ AGENT-001 (Database) : Insertions, indexes, contraintes
         ├──→ AGENT-005 (Categorization) : Auto-cat post-import
         ├──→ AGENT-016 (Notifications) : Progression, erreurs
         ├──→ AGENT-002 (Security) : Validation fichiers, scan virus
         └──→ AGENT-009/010 (UI) : Import wizard, visualisation
```

### Points d'intégration

```python
# Post-import → AGENT-005
from modules.categorization_cascade import categorize_pending_transactions
categorize_pending_transactions(source='import_batch', batch_id=migration_id)

# Progress → AGENT-016
from modules.notifications import create_progress_notification
create_progress_notification(
    type="import_progress",
    title=f"Import {migration_name}",
    current=processed,
    total=total
)
```

---

## 📚 Références

### Formats Supportés - Détails Techniques

| Format | Extension | Encodage | Séparateur décimal | Dates | Complexité |
|--------|-----------|----------|-------------------|-------|------------|
| **CSV** | .csv | Auto (UTF-8/Latin-1/CP1252) | Auto (.,) | Multi-format | ⭐ |
| **QIF** | .qif | ASCII/UTF-8 | Point | US/EU | ⭐⭐ |
| **OFX** | .ofx, .qfx | UTF-8 | Point | YYYYMMDD | ⭐⭐ |
| **Excel** | .xlsx, .xls | Binary | Variable | Cell format | ⭐ |
| **JSON** | .json | UTF-8 | Point | ISO 8601 | ⭐ |
| **JSONL** | .jsonl | UTF-8 | Point | ISO 8601 | ⭐ |

### Outils Concurrents - Migration Supportée

| Outil | Format Export | Qualité données | Notes |
|-------|--------------|-----------------|-------|
| **Bankin'** | JSON API | ⭐⭐⭐⭐⭐ | API officielle, structure propre |
| **Linxo** | CSV, OFX | ⭐⭐⭐⭐ | Bon export, catégories perso |
| **Fintonic** | CSV | ⭐⭐⭐ | Format simple, moins de métadonnées |
| **MoneyWiz** | QIF, CSV | ⭐⭐⭐⭐ | QIF bien structuré |
| **YNAB** | CSV | ⭐⭐⭐⭐ | Export propre |

### Schéma Base de Données Étendu

```sql
-- Transactions avec traçabilité migration
ALTER TABLE transactions ADD COLUMN migration_id TEXT;
ALTER TABLE transactions ADD COLUMN source_format TEXT;
ALTER TABLE transactions ADD COLUMN source_hash TEXT;
ALTER TABLE transactions ADD COLUMN imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE transactions ADD COLUMN validated BOOLEAN DEFAULT FALSE;

-- Index pour performance
CREATE INDEX idx_transactions_migration ON transactions(migration_id);
CREATE INDEX idx_transactions_source_hash ON transactions(source_hash);
CREATE INDEX idx_transactions_imported_at ON transactions(imported_at);

-- Table de suivi des migrations
CREATE TABLE migration_tracking (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    records_total INTEGER,
    records_imported INTEGER,
    records_failed INTEGER,
    metadata JSON
);
```

### Métriques & SLAs

| Métrique | Target | Alerte | Critique |
|----------|--------|--------|----------|
| Taux réussite import | >98% | <95% | <90% |
| Temps import (1k lignes) | <5s | >10s | >30s |
| Doublons créés | <0.1% | >1% | >5% |
| Erreurs silencieuses | 0 | >0 | - |
| Temps rollback | <2min | >5min | >10min |

---

**Agent spécialisé AGENT-017** - Data Pipeline & Migration Specialist  
_Version 2.0 - Architecture complète ETL_  
_Couvre 99% des besoins migration et import pour FinancePerso_
