"""
Local ML Module - Catégorisation de transactions avec scikit-learn

Ce module fournit une alternative locale à l'API IA pour la catégorisation
des transactions financières. Utilise scikit-learn pour un modèle léger
de classification de texte.
"""

import os
import pickle
import re
from datetime import datetime
from typing import Optional, Tuple, List
import numpy as np

# Gestion optionnelle de scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories
from modules.logger import logger

# Chemin du modèle sauvegardé
MODEL_PATH = "Data/local_ml_model.pkl"


class LocalTransactionClassifier:
    """
    Classificateur local de transactions financières.
    Utilise un pipeline TF-IDF + Naive Bayes pour la classification de texte.
    """
    
    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.is_trained = False
        self.categories: List[str] = []
        self.training_date: Optional[datetime] = None
        
        # Essayer de charger un modèle existant
        self._load_model()
    
    def _preprocess_label(self, label: str) -> str:
        """
        Prétraite le libellé de transaction pour le ML.
        - Met en majuscules
        - Supprime les numéros de carte, dates
        - Garde les mots significatifs
        """
        if not label:
            return ""
        
        text = label.upper()
        
        # Patterns à supprimer
        patterns = [
            r'CARTE\s*\*?\d*',           # CARTE, CARTE*1234
            r'CB\s*\*?\d*',               # CB, CB*1234
            r'\d{2}/\d{2}/\d{2,4}',       # Dates 31/01/2024
            r'\d{4}\*\d{4}\*\d{4}',       # Numéros de carte masqués
            r'VIR\s*(?:INST)?\s*(?:TR)?', # Virement, VIR INST
            r'PRLV\s*(?:SEPA)?',          # Prélèvement
            r'\d{2,}',                    # Nombres longs (montants, références)
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, ' ', text)
        
        # Nettoyage final
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def train(self, min_samples_per_category: int = 5) -> Tuple[bool, str]:
        """
        Entraîne le modèle sur les transactions historiques.
        
        Args:
            min_samples_per_category: Nombre minimum d'exemples par catégorie
            
        Returns:
            (succès, message)
        """
        if not SKLEARN_AVAILABLE:
            return False, "scikit-learn n'est pas installé. Installez-le avec: pip install scikit-learn"
        
        try:
            # Récupérer les transactions étiquetées
            df = get_all_transactions()
            
            if df.empty:
                return False, "Pas de données d'entraînement disponibles"
            
            # Filtrer les transactions validées avec une catégorie
            df = df[df['status'] == 'validated']
            df = df[df['category_validated'].notna()]
            df = df[df['category_validated'] != 'Inconnu']
            
            if len(df) < 10:
                return False, f"Pas assez de transactions validées ({len(df)}). Minimum: 10"
            
            # Compter les exemples par catégorie
            category_counts = df['category_validated'].value_counts()
            valid_categories = category_counts[category_counts >= min_samples_per_category].index.tolist()
            
            if len(valid_categories) < 2:
                return False, f"Pas assez de catégories avec {min_samples_per_category}+ exemples"
            
            # Filtrer sur les catégories valides
            df = df[df['category_validated'].isin(valid_categories)]
            
            # Préparer les données
            X = df['label'].apply(self._preprocess_label).values
            y = df['category_validated'].values
            
            self.categories = valid_categories
            
            # Créer le pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),  # Unigrams et bigrams
                    min_df=2,            # Ignorer les termes trop rares
                    max_df=0.8           # Ignorer les termes trop fréquents
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            # Entraîner
            self.model.fit(X, y)
            self.is_trained = True
            self.training_date = datetime.now()
            
            # Évaluer sur un split de test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Sauvegarder le modèle
            self._save_model()
            
            logger.info(f"Local ML model trained: {len(valid_categories)} categories, {len(df)} samples, {accuracy:.2%} accuracy")
            
            return True, f"Modèle entraîné sur {len(df)} transactions, {len(valid_categories)} catégories. Précision: {accuracy:.1%}"
            
        except Exception as e:
            logger.error(f"Error training local ML model: {e}")
            return False, f"Erreur d'entraînement: {str(e)}"
    
    def predict(self, label: str, amount: float = None, date=None) -> Tuple[Optional[str], float]:
        """
        Prédit la catégorie d'une transaction.
        
        Args:
            label: Libellé de la transaction
            amount: Montant (optionnel, pour info)
            date: Date (optionnelle, pour info)
            
        Returns:
            (catégorie prédite, confiance)
        """
        if not self.is_trained or self.model is None:
            return None, 0.0
        
        try:
            processed_label = self._preprocess_label(label)
            
            if not processed_label:
                return None, 0.0
            
            # Prédiction
            prediction = self.model.predict([processed_label])[0]
            
            # Calculer la confiance (probabilité max)
            proba = self.model.predict_proba([processed_label])[0]
            confidence = float(np.max(proba))
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"Error predicting with local ML: {e}")
            return None, 0.0
    
    def predict_batch(self, labels: List[str]) -> List[Tuple[Optional[str], float]]:
        """
        Prédit les catégories pour plusieurs transactions.
        
        Args:
            labels: Liste des libellés
            
        Returns:
            Liste de (catégorie, confiance)
        """
        if not self.is_trained or self.model is None:
            return [(None, 0.0)] * len(labels)
        
        try:
            processed = [self._preprocess_label(l) for l in labels]
            predictions = self.model.predict(processed)
            probas = self.model.predict_proba(processed)
            
            results = []
            for pred, proba in zip(predictions, probas):
                confidence = float(np.max(proba))
                results.append((pred, confidence))
            
            return results
            
        except Exception as e:
            logger.error(f"Error batch predicting: {e}")
            return [(None, 0.0)] * len(labels)
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du modèle."""
        return {
            'is_trained': self.is_trained,
            'categories_count': len(self.categories),
            'categories': self.categories,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'model_path': MODEL_PATH,
            'model_exists': os.path.exists(MODEL_PATH),
            'sklearn_available': SKLEARN_AVAILABLE
        }
    
    def _save_model(self):
        """Sauvegarde le modèle sur disque."""
        if self.model is None:
            return
        
        try:
            model_data = {
                'model': self.model,
                'categories': self.categories,
                'training_date': self.training_date,
                'version': '1.0'
            }
            
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model_data, f)
                
            logger.info(f"Local ML model saved to {MODEL_PATH}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Charge le modèle depuis le disque."""
        if not os.path.exists(MODEL_PATH):
            return
        
        try:
            with open(MODEL_PATH, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data.get('model')
            self.categories = model_data.get('categories', [])
            self.training_date = model_data.get('training_date')
            self.is_trained = self.model is not None
            
            logger.info(f"Local ML model loaded from {MODEL_PATH}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_trained = False
    
    def retrain_if_needed(self, min_accuracy: float = 0.7) -> Tuple[bool, str]:
        """
        Réentraîne le modèle si nécessaire.
        
        Args:
            min_accuracy: Précision minimale requise
            
        Returns:
            (modèle mis à jour, message)
        """
        # Si pas de modèle, entraîner
        if not self.is_trained:
            return self.train()
        
        # Si le modèle date de plus de 7 jours, réentraîner
        if self.training_date:
            days_since_training = (datetime.now() - self.training_date).days
            if days_since_training > 7:
                logger.info(f"Model is {days_since_training} days old, retraining...")
                return self.train()
        
        return False, "Modèle à jour, pas de réentraînement nécessaire"


# Instance globale du classificateur
_classifier: Optional[LocalTransactionClassifier] = None


def get_classifier() -> LocalTransactionClassifier:
    """Retourne l'instance globale du classificateur."""
    global _classifier
    if _classifier is None:
        _classifier = LocalTransactionClassifier()
    return _classifier


def predict_category_local(label: str, amount: float = None, date=None) -> Tuple[Optional[str], float]:
    """
    Fonction helper pour prédire la catégorie d'une transaction.
    
    Returns:
        (catégorie, confiance)
    """
    classifier = get_classifier()
    return classifier.predict(label, amount, date)


def train_local_model() -> Tuple[bool, str]:
    """
    Entraîne le modèle local sur les transactions historiques.
    
    Returns:
        (succès, message)
    """
    classifier = get_classifier()
    return classifier.train()


def get_local_ml_stats() -> dict:
    """Retourne les statistiques du modèle local."""
    classifier = get_classifier()
    return classifier.get_stats()


def is_local_ml_available() -> bool:
    """Vérifie si le ML local est disponible (scikit-learn installé)."""
    return SKLEARN_AVAILABLE
