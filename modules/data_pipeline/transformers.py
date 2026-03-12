"""
Transformateurs de données pour le pipeline d'import.
"""

import re
from datetime import datetime


class DateNormalizer:
    """Normalise les dates vers le format ISO."""
    
    FORMATS = [
        '%Y-%m-%d',      # 2024-01-15
        '%d/%m/%Y',      # 15/01/2024
        '%d/%m/%y',      # 15/01/24
        '%m/%d/%Y',      # 01/15/2024
        '%d-%m-%Y',      # 15-01-2024
        '%Y%m%d',        # 20240115
        '%d.%m.%Y',      # 15.01.2024
        '%Y/%m/%d',      # 2024/01/15
    ]
    
    @classmethod
    def normalize(cls, date_str: str) -> str:
        """
        Normalise une date au format ISO (YYYY-MM-DD).
        
        Args:
            date_str: Date en entrée
            
        Returns:
            Date au format ISO
            
        Raises:
            ValueError: Si le format n'est pas reconnu
        """
        if not date_str:
            raise ValueError("Date manquante")
        
        date_str = str(date_str).strip()
        
        for fmt in cls.FORMATS:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        raise ValueError(f"Format de date non reconnu: {date_str}")
    
    @classmethod
    def detect_format(cls, sample_dates: list[str]) -> str:
        """
        Détecte le format de date le plus probable.
        
        Args:
            sample_dates: Échantillon de dates
            
        Returns:
            Format détecté
        """
        for fmt in cls.FORMATS:
            success = 0
            for date_str in sample_dates:
                try:
                    datetime.strptime(str(date_str).strip(), fmt)
                    success += 1
                except ValueError:
                    break
            
            if success == len(sample_dates):
                return fmt
        
        return '%Y-%m-%d'  # Default


class AmountNormalizer:
    """Normalise les montants."""
    
    @staticmethod
    def normalize(amount_str: str, decimal_separator: str = None) -> float:
        """
        Normalise un montant en float.
        
        Args:
            amount_str: Montant en entrée
            decimal_separator: Séparateur décimal forcé (',' ou '.')
            
        Returns:
            Montant en float
        """
        if not amount_str:
            raise ValueError("Montant manquant")
        
        # Nettoyer
        amount_str = str(amount_str).replace(' ', '').replace('€', '').replace('$', '')
        
        # Détecter si deux séparateurs présents
        if ',' in amount_str and '.' in amount_str:
            # Déterminer quel est le séparateur de milliers
            last_comma = amount_str.rfind(',')
            last_dot = amount_str.rfind('.')
            
            if last_comma > last_dot:
                # Format FR: 1.234,56
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                # Format US: 1,234.56
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Potentiellement séparateur décimal FR
            if decimal_separator == ',':
                amount_str = amount_str.replace(',', '.')
            elif decimal_separator == '.':
                amount_str = amount_str.replace(',', '')
            else:
                # Auto-détection: si plus d'un chiffre après la virgule
                parts = amount_str.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    amount_str = amount_str.replace(',', '.')
                else:
                    amount_str = amount_str.replace(',', '')
        
        return float(amount_str)
    
    @staticmethod
    def normalize_with_sign(amount: float, transaction_type: str = None) -> float:
        """
        Normalise le signe d'un montant.
        
        Les dépenses doivent être négatives, les revenus positifs.
        
        Args:
            amount: Montant brut
            transaction_type: Type de transaction ('debit', 'credit', 'expense', 'income')
            
        Returns:
            Montant avec signe correct
        """
        if transaction_type:
            transaction_type = transaction_type.lower()
            if transaction_type in ('debit', 'expense', 'withdrawal'):
                return -abs(amount)
            elif transaction_type in ('credit', 'income', 'deposit'):
                return abs(amount)
        
        return amount


class CategoryMapper:
    """Mappe les catégories externes vers les catégories FinancePerso."""
    
    # Mapping par défaut pour les catégories courantes
    DEFAULT_MAPPING = {
        # Bankin'/Linxo
        'alimentation': 'Alimentation',
        'restaurant': 'Restaurants',
        'transport': 'Transport',
        'essence': 'Transport',
        'sante': 'Santé',
        'pharmacie': 'Santé',
        'loisirs': 'Loisirs',
        'shopping': 'Shopping',
        'habillement': 'Shopping',
        'logement': 'Logement',
        'loyer': 'Logement',
        'factures': 'Factures',
        'electricite': 'Factures',
        'telephone': 'Factures',
        'revenus': 'Revenus',
        'salaire': 'Revenus',
        'virement': 'Transferts',
        
        # YNAB
        'immediate obligations': 'Factures',
        'true expenses': 'Dépenses récurrentes',
        'debt payments': 'Dettes',
        'quality of life': 'Loisirs',
        'just for fun': 'Loisirs',
        'income': 'Revenus',
    }
    
    def __init__(self, custom_mapping: dict[str, str] = None):
        self.mapping = {**self.DEFAULT_MAPPING, **(custom_mapping or {})}
    
    def map_category(self, external_category: str) -> str | None:
        """
        Mappe une catégorie externe vers une catégorie interne.
        
        Args:
            external_category: Nom de la catégorie externe
            
        Returns:
            Nom de la catégorie interne, ou None si non trouvée
        """
        if not external_category:
            return None
        
        # Normaliser la clé
        key = external_category.lower().strip()
        
        # Recherche exacte
        if key in self.mapping:
            return self.mapping[key]
        
        # Recherche partielle
        for ext_key, int_cat in self.mapping.items():
            if ext_key in key or key in ext_key:
                return int_cat
        
        return None
    
    def add_mapping(self, external: str, internal: str):
        """Ajoute un mapping personnalisé."""
        self.mapping[external.lower().strip()] = internal
    
    def get_unknown_categories(self, external_categories: list[str]) -> list[str]:
        """
        Retourne les catégories externes non reconnues.
        
        Args:
            external_categories: Liste des catégories à vérifier
            
        Returns:
            Liste des catégories non mappées
        """
        unknown = []
        for cat in external_categories:
            if cat and not self.map_category(cat):
                unknown.append(cat)
        return list(set(unknown))


class LabelCleaner:
    """Nettoie et normalise les libellés de transactions."""
    
    # Patterns à supprimer
    NOISE_PATTERNS = [
        r'\bCB\s*',           # CB
        r'\bTPE\s*',          # TPE
        r'\bRETRAIT\s*',      # RETRAIT
        r'\bVIR\s*',          # VIREMENT
        r'\bPRLV\s*',         # PRELEVEMENT
        r'\d{2}/\d{2}/\d{2,4}',  # Dates
        r'\d{4}\*{2}\d{4}',    # Numéros de carte masqués
        r'\*{4,}',             # Étoiles
    ]
    
    # Mots à supprimer
    NOISE_WORDS = [
        'du', 'le', 'la', 'les', 'de', 'des', 'et', 'en', 'à', 'au',
        'carte', 'paiement', 'facture', 'prélèvement', 'virement'
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.NOISE_PATTERNS]
    
    def clean(self, label: str) -> str:
        """
        Nettoie un libellé.
        
        Args:
            label: Libellé brut
            
        Returns:
            Libellé nettoyé
        """
        if not label:
            return "TRANSACTION SANS LIBELLE"
        
        label = str(label)
        
        # Supprimer les patterns bruyants
        for pattern in self.patterns:
            label = pattern.sub(' ', label)
        
        # Mettre en majuscules
        label = label.upper()
        
        # Supprimer les mots inutiles (optionnel, peut être trop agressif)
        # words = label.split()
        # words = [w for w in words if w not in self.NOISE_WORDS]
        # label = ' '.join(words)
        
        # Normaliser les espaces
        label = ' '.join(label.split())
        
        return label.strip()
    
    def extract_merchant(self, label: str) -> str | None:
        """
        Extrait le nom du commerçant d'un libellé.
        
        Args:
            label: Libellé de transaction
            
        Returns:
            Nom du commerçant, ou None
        """
        cleaned = self.clean(label)
        
        # Patterns communs de commerçants
        merchant_patterns = [
            r'(CARREFOUR|LECLERC|AUCHAN|LIDL|ALDI|CASINO)',
            r'(MACDONALD|KFC|BURGER KING|SUBWAY|STARBUCKS)',
            r'(DECATHLON|GO SPORT|INTERSPORT)',
            r'(FNAC|DARTY|BOULANGER|CONFORAMA)',
            r'(PHARMACIE|PHIE)',
            r'(TOTAL|SHELL|BP|ESSO)',
        ]
        
        for pattern in merchant_patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
