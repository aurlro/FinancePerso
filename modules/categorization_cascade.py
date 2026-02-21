"""
Cascade de Confiance - Catégorisation intelligente
==================================================

Système de catégorisation en cascade pour minimiser les appels IA:

1. Heuristique (règles dur) → 2. Similarité (historique) → 3. IA (cloud/local)

La similarité utilise difflib.SequenceMatcher pour comparer les libellés
aux transactions déjà catégorisées en base.

Usage:
    from modules.categorization_cascade import TransactionCategorizer
    
    categorizer = TransactionCategorizer()
    result = categorizer.categorize("CARREFOUR PARIS 15", amount=-45.67)
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Optional

import pandas as pd

from modules.db_v2 import CategoryRepository, TransactionRepository
from modules.logger import logger


@dataclass
class CategorizationResult:
    """Résultat d'une catégorisation."""
    
    category: str
    clean_merchant: str
    confidence_score: float
    source: str  # "heuristic", "similarity", "local_ai", "cloud_ai"
    is_recurring_candidate: bool = False
    risk_flag: int = 0
    similar_transaction_id: Optional[int] = None
    similarity_score: Optional[float] = None


class TransactionCategorizer:
    """
    Catégorisateur de transactions avec cascade de confiance.
    
    Ordre de traitement:
    1. Règles heuristiques (patterns connus)
    2. Similarité avec historique (SequenceMatcher > 0.85)
    3. IA locale (Llama 3.2 3B)
    4. IA cloud (Gemini/DeepSeek fallback)
    
    Attributes:
        similarity_threshold: Seuil pour réutiliser catégorie existante
        min_confidence: Confiance minimale pour accepter résultat IA
    """

    # Taxonomie PFCv2 (Personal Finance Categories v2)
    PFCV2_CATEGORIES = {
        "Food & Drink": [
            "Groceries",
            "Restaurants",
            "Fast Food",
            "Coffee Shops",
            "Bars",
            "Food Delivery",
        ],
        "Transportation": [
            "Fuel",
            "Public Transit",
            "Taxi & Rideshare",
            "Parking",
            "Tolls",
            "Vehicle Maintenance",
        ],
        "Shopping": [
            "Clothing",
            "Electronics",
            "Home & Garden",
            "Books & Hobbies",
            "Sporting Goods",
            "Gifts",
        ],
        "Financial": [
            "Bank Fees",
            "Interest",
            "Investments",
            "Insurance",
            "Loans",
        ],
        "Housing": [
            "Rent",
            "Mortgage",
            "Utilities",
            "Internet",
            "Phone",
            "Home Improvement",
            "Home Insurance",
        ],
        "Health": [
            "Medical",
            "Pharmacy",
            "Dental",
            "Vision",
            "Health Insurance",
            "Gym & Fitness",
        ],
        "Entertainment": [
            "Streaming",
            "Movies & Shows",
            "Games",
            "Music",
            "Events & Concerts",
            "Subscriptions",
        ],
        "Education": [
            "Tuition",
            "Books & Supplies",
            "Courses",
            "Student Loans",
        ],
        "Income": [
            "Salary",
            "Freelance",
            "Investments",
            "Refunds",
            "Gifts Received",
        ],
        "Transfers": [
            "Internal Transfer",
            "External Transfer",
            "Savings",
            "Investment Transfer",
        ],
    }

    # Patterns heuristiques (règles dur)
    HEURISTIC_PATTERNS = {
        # Food & Drink
        r"(?i)(carrefour|auchan|leclerc|lidl|aldi|casino|monoprix|franprix|intermarche)": 
            ("Food & Drink", "Groceries"),
        r"(?i)(macdo|mcdonald|burger king|kfc|subway|quick|five guys)": 
            ("Food & Drink", "Fast Food"),
        r"(?i)(starbuck|costa|pret|paul|eric kayser|boulangerie|patisserie)": 
            ("Food & Drink", "Coffee Shops"),
        r"(?i)(uber eat|deliveroo|just eat|foodchery|stuart)": 
            ("Food & Drink", "Food Delivery"),
        
        # Transportation
        r"(?i)(total|shell|bp|esso|avia|e.leclerc essence|carrefour essence)": 
            ("Transportation", "Fuel"),
        r"(?i)(uber|bolt|taxi|g7|allocab|marcel|heetch|kapten)": 
            ("Transportation", "Taxi & Rideshare"),
        r"(?i)(ratp|sncf|transilien|metro|bus|tram|navigo)": 
            ("Transportation", "Public Transit"),
        r"(?i)(parking|indigo|saemes)": 
            ("Transportation", "Parking"),
        
        # Financial
        r"(?i)(agios|frais|commission|interet|cheque|virement|prelevement)": 
            ("Financial", "Bank Fees"),
        r"(?i)(assurance|axa|maif|macif|gmf|groupama)": 
            ("Financial", "Insurance"),
        
        # Housing
        r"(?i)(edf|engie|direct energie|total energie|veolia|suez)": 
            ("Housing", "Utilities"),
        r"(?i)(orange|sfr|bouygues|free mobile|sosh|red)": 
            ("Housing", "Phone"),
        r"(?i)(orange|sfr|free|bouygues telecom.*box|sosh.*box)": 
            ("Housing", "Internet"),
        
        # Entertainment
        r"(?i)(netflix|spotify|amazon prime|disney|apple tv|youtube| Canal)": 
            ("Entertainment", "Streaming"),
        r"(?i)(cinema|ugc|gaumont|pathe|mk2)": 
            ("Entertainment", "Movies & Shows"),
        
        # Health
        r"(?i)(pharmacie|pharmacy|parapharmacie)": 
            ("Health", "Pharmacy"),
        r"(?i)(doctolib|medecin|dentiste|ophtalmo|kine|osteopathe)": 
            ("Health", "Medical"),
        r"(?i)(basic fit|keep cool|neoness|fitness park|gym)": 
            ("Health", "Gym & Fitness"),
        
        # Income patterns (positive amounts)
        r"(?i)(salaire|virement.*employeur|paye|remuneration)": 
            ("Income", "Salary"),
        r"(?i)(remboursement|rembourse|retrocession)": 
            ("Income", "Refunds"),
    }

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        min_confidence: float = 0.7,
        use_local_ai: bool = True,
        use_cloud_fallback: bool = True,
    ):
        """
        Initialize le catégoriseur.
        
        Args:
            similarity_threshold: Seuil SequenceMatcher (0-1)
            min_confidence: Confiance minimale résultat IA
            use_local_ai: Utiliser SLM local si disponible
            use_cloud_fallback: Fallback sur cloud si local échoue
        """
        self.similarity_threshold = similarity_threshold
        self.min_confidence = min_confidence
        self.use_local_ai = use_local_ai
        self.use_cloud_fallback = use_cloud_fallback
        
        # Repositories
        self.tx_repo = TransactionRepository()
        self.cat_repo = CategoryRepository()
        
        # Cache historique
        self._history_cache: Optional[pd.DataFrame] = None
        
        # Provider IA (lazy load)
        self._local_provider = None
        self._cloud_provider = None

    def _get_local_provider(self):
        """Lazy load du provider IA local."""
        if self._local_provider is None and self.use_local_ai:
            try:
                from modules.ai.local_slm_provider import get_local_slm_provider
                self._local_provider = get_local_slm_provider(fallback_to_cloud=False)
            except Exception as e:
                logger.warning(f"Could not load local AI: {e}")
                self._local_provider = None
        return self._local_provider

    def _get_cloud_provider(self):
        """Lazy load du provider cloud."""
        if self._cloud_provider is None and self.use_cloud_fallback:
            try:
                from modules.ai_manager_v2 import get_ai_provider
                self._cloud_provider = get_ai_provider()
            except Exception as e:
                logger.warning(f"Could not load cloud AI: {e}")
                self._cloud_provider = None
        return self._cloud_provider

    def _load_history(self) -> pd.DataFrame:
        """Charge l'historique des transactions catégorisées."""
        if self._history_cache is None:
            self._history_cache = self.tx_repo.get_all(
                filters={"status": "validated"},
                limit=5000,  # Dernières 5000 transactions
            )
        return self._history_cache

    def _clean_label(self, label: str) -> str:
        """Nettoie le libellé pour comparaison."""
        # Remove extra spaces, normalize case
        cleaned = re.sub(r'\s+', ' ', label.strip().upper())
        # Remove common prefixes
        cleaned = re.sub(r'^(CB|VIR|PRLV|RETRAIT|CHEQUE)\s*', '', cleaned)
        return cleaned

    def _check_heuristics(self, label: str, amount: float) -> Optional[CategorizationResult]:
        """
        Étape 1: Vérifie les règles heuristiques.
        
        Returns:
            Résultat si pattern match, None sinon
        """
        cleaned = self._clean_label(label)
        
        for pattern, (category, subcategory) in self.HEURISTIC_PATTERNS.items():
            if re.search(pattern, cleaned):
                # Determine if income based on amount
                if category == "Income" and amount < 0:
                    continue  # Income should be positive
                if category != "Income" and amount > 0:
                    # Could be refund, keep checking
                    pass
                
                return CategorizationResult(
                    category=f"{category} > {subcategory}",
                    clean_merchant=self._extract_merchant(label),
                    confidence_score=0.95,
                    source="heuristic",
                    is_recurring_candidate=self._is_recurring_pattern(label),
                )
        
        return None

    def _check_similarity(self, label: str) -> Optional[CategorizationResult]:
        """
        Étape 2: Compare avec l'historique via SequenceMatcher.
        
        Returns:
            Résultat si similarité > threshold, None sinon
        """
        history = self._load_history()
        if history.empty:
            return None
        
        cleaned_input = self._clean_label(label)
        best_match = None
        best_score = 0.0
        best_tx_id = None
        
        for _, row in history.iterrows():
            hist_label = str(row.get('label', ''))
            cleaned_hist = self._clean_label(hist_label)
            
            # Calculate similarity
            similarity = SequenceMatcher(None, cleaned_input, cleaned_hist).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = row
                best_tx_id = row.get('id')
        
        if best_score >= self.similarity_threshold and best_match is not None:
            category = best_match.get('category_validated') or best_match.get('category', 'Unknown')
            
            return CategorizationResult(
                category=category,
                clean_merchant=self._extract_merchant(label),
                confidence_score=round(best_score, 3),
                source="similarity",
                similar_transaction_id=best_tx_id,
                similarity_score=round(best_score, 3),
                is_recurring_candidate=self._is_recurring_pattern(label),
            )
        
        return None

    def _call_ai(self, label: str, amount: float, date: str) -> CategorizationResult:
        """
        Étape 3: Appelle l'IA (local ou cloud).
        """
        # Build structured prompt
        prompt = self._build_ai_prompt(label, amount, date)
        
        # Try local first
        if self.use_local_ai:
            local = self._get_local_provider()
            if local and local._model_loaded:
                try:
                    result = local.generate_json(prompt, temperature=0.1)
                    return self._parse_ai_result(result, "local_ai")
                except Exception as e:
                    logger.warning(f"Local AI failed: {e}")
        
        # Fallback to cloud
        if self.use_cloud_fallback:
            cloud = self._get_cloud_provider()
            if cloud:
                try:
                    result = cloud.generate_json(prompt)
                    return self._parse_ai_result(result, "cloud_ai")
                except Exception as e:
                    logger.error(f"Cloud AI failed: {e}")
        
        # Ultimate fallback: unknown
        return CategorizationResult(
            category="Unknown",
            clean_merchant=self._extract_merchant(label),
            confidence_score=0.0,
            source="fallback",
        )

    def _build_ai_prompt(self, label: str, amount: float, date: str) -> str:
        """
        Construit le prompt pour l'IA au format PFCv2.
        """
        categories_list = "\n".join([
            f"  - {main}: {', '.join(subs)}"
            for main, subs in self.PFCV2_CATEGORIES.items()
        ])
        
        prompt = f"""Analyse cette transaction bancaire et extrait les informations structurées.

DONNÉES BRUTES:
- Libellé: "{label}"
- Montant: {amount:.2f} EUR
- Date: {date}

TAXONOMIE PFCv2 (utilise ce format: "Main Category > Subcategory"):
{categories_list}

INSTRUCTIONS:
1. Nettoie le nom du marchand (retire les codes, numéros de transaction)
2. Catégorise selon la taxonomie PFCv2 exacte
3. Détecte si c'est une transaction récurrente potentielle
4. Évalue le risque (0=faible, 1=moyen, 2=élevé, 3=suspect)
5. Fournis un score de confiance (0.0-1.0)

RÉPONDS UNIQUEMENT AVEC CE JSON (pas de texte avant/après):
{{
  "transaction_id": "auto",
  "clean_merchant": "string",
  "category": "Main Category > Subcategory",
  "is_recurring_candidate": boolean,
  "risk_flag": integer (0-3),
  "confidence_score": float
}}"""
        return prompt

    def _parse_ai_result(self, result: dict, source: str) -> CategorizationResult:
        """Parse le résultat JSON de l'IA."""
        if "error" in result:
            logger.warning(f"AI returned error: {result['error']}")
            return CategorizationResult(
                category="Unknown",
                clean_merchant="Unknown",
                confidence_score=0.0,
                source="error",
            )
        
        return CategorizationResult(
            category=result.get("category", "Unknown"),
            clean_merchant=result.get("clean_merchant", "Unknown"),
            confidence_score=result.get("confidence_score", 0.5),
            source=source,
            is_recurring_candidate=result.get("is_recurring_candidate", False),
            risk_flag=result.get("risk_flag", 0),
        )

    def _extract_merchant(self, label: str) -> str:
        """Extrait le nom du marchand d'un libellé."""
        # Remove transaction codes
        cleaned = re.sub(r'\b(CB|VIR|PRLV|RETRAIT|CHEQUE)\s*\d*\s*', '', label)
        # Remove dates
        cleaned = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', cleaned)
        # Remove amounts
        cleaned = re.sub(r'\d+[.,]\d{2}\s*(EUR|€)?', '', cleaned)
        # Clean up
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned[:50] if cleaned else "Unknown"

    def _is_recurring_pattern(self, label: str) -> bool:
        """Détecte si le libellé correspond à un pattern récurrent."""
        recurring_keywords = [
            r'(?i)(abonnement|subscription)',
            r'(?i)(mensuel|monthly|annuel|yearly)',
            r'(?i)(prélèvement|prelevement).*automatique',
            r'(?i)(netflix|spotify|prime|disney|canal)',
            r'(?i)(edf|engie|orange|sfr|free)',
            r'(?i)(assurance|mutuelle|cotisation)',
        ]
        return any(re.search(pattern, label) for pattern in recurring_keywords)

    def categorize(
        self,
        label: str,
        amount: float = 0.0,
        date: str = "",
        force_ai: bool = False,
    ) -> CategorizationResult:
        """
        Catégorise une transaction via la cascade de confiance.
        
        Ordre de traitement:
        1. Heuristique (patterns connus)
        2. Similarité avec historique (SequenceMatcher > 0.85)
        3. IA locale (Llama 3.2)
        4. IA cloud (fallback)
        
        Args:
            label: Libellé brut de la transaction
            amount: Montant (négatif pour dépense, positif pour revenu)
            date: Date de la transaction
            force_ai: Forcer l'utilisation de l'IA (skip heuristique/similarité)
            
        Returns:
            CategorizationResult avec catégorie, confiance, source
        """
        logger.info(f"Categorizing: '{label[:50]}...' ({amount:.2f} EUR)")
        
        # Step 1: Heuristics (unless forced AI)
        if not force_ai:
            result = self._check_heuristics(label, amount)
            if result:
                logger.info(f"✅ Heuristic match: {result.category} ({result.confidence_score})")
                return result
        
        # Step 2: Similarity (unless forced AI)
        if not force_ai:
            result = self._check_similarity(label)
            if result:
                logger.info(f"✅ Similarity match: {result.category} (score: {result.similarity_score})")
                return result
        
        # Step 3 & 4: AI (local then cloud)
        logger.info("🤖 Using AI categorization")
        result = self._call_ai(label, amount, date)
        logger.info(f"✅ AI result: {result.category} ({result.source}, conf: {result.confidence_score})")
        
        return result

    def invalidate_cache(self):
        """Invalide le cache historique."""
        self._history_cache = None
        logger.info("Categorizer cache invalidated")


# Convenience function
def categorize_transaction(
    label: str,
    amount: float = 0.0,
    date: str = "",
) -> dict[str, Any]:
    """
    Catégorise une transaction (fonction simple).
    
    Returns:
        Dict avec category, clean_merchant, confidence, source
    """
    categorizer = TransactionCategorizer()
    result = categorizer.categorize(label, amount, date)
    
    return {
        "category": result.category,
        "clean_merchant": result.clean_merchant,
        "confidence_score": result.confidence_score,
        "source": result.source,
        "is_recurring_candidate": result.is_recurring_candidate,
        "risk_flag": result.risk_flag,
        "similarity_score": result.similarity_score,
    }
