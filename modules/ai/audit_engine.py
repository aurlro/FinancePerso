"""
Audit Engine - Logique métier pour l'audit des transactions.
Détecte les incohérences, anomalies et erreurs de catégorisation.
"""

import json
from typing import Any

import pandas as pd

from modules.ai_manager import get_active_model_name, get_ai_provider
from modules.categorization import clean_label
from modules.logger import logger


def detect_inconsistencies(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Find labels that have been categorized differently across transactions.

    Args:
        df: DataFrame with transaction data

    Returns:
        List of inconsistency dictionaries
    """
    if df.empty:
        return []

    # Create a clean label column for grouping
    df = df.copy()
    df["clean"] = df["label"].apply(clean_label)

    # Filter only validated or relevant categories
    df_valid = df[
        (df["status"] != "pending")
        & (~df["category_validated"].isin(["Virement Interne", "Hors Budget"]))
    ].copy()

    if df_valid.empty:
        return []

    # Group by clean label
    grouped = df_valid.groupby("clean")["category_validated"].unique()

    inconsistencies = []

    for label, categories in grouped.items():
        # Filter out 'Inconnu' if we have other valid categories
        cats = [c for c in categories if c and c != "Inconnu" and c != ""]
        if len(set(cats)) > 1:
            # Found same label with different categories
            examples = df_valid[df_valid["clean"] == label][
                ["id", "date", "label", "amount", "category_validated"]
            ]
            inconsistencies.append(
                {
                    "type": "Incohérence",
                    "label": label,
                    "details": f"Classé comme : {', '.join(cats)}",
                    "categories": cats,
                    "rows": examples,
                }
            )

    return inconsistencies


def ai_audit_batch(df: pd.DataFrame, limit: int = 50) -> list[dict[str, Any]]:
    """
    Send unique label/category pairs to AI to check for logical errors.

    Args:
        df: DataFrame with transactions
        limit: Maximum number of pairs to analyze (for performance)

    Returns:
        List of AI-detected issues
    """
    if df.empty:
        return []

    # Get unique pairs of (clean_label, category)
    df = df.copy()
    df["clean"] = df["label"].apply(clean_label)
    unique_pairs = df[["clean", "category_validated"]].drop_duplicates()

    # Limit for performance
    unique_pairs = unique_pairs.head(limit)

    prompt_data = unique_pairs.to_dict(orient="records")

    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()

        prompt = f"""
        Analyse ces paires (Libellé, Catégorie) et identifie celles qui semblent ERRONÉES.
        Ignore les cas ambigus, concentre-toi sur les erreurs flagrantes 
        (ex: 'McDonalds' en 'Santé', 'Impôts' en 'Loisirs').
        
        Données : {json.dumps(prompt_data, ensure_ascii=False)}
        
        Réponds uniquement en JSON (liste d'objets) :
        [
            {{ "clean": "Libellé", "current": "Catégorie actuelle", 
               "suggested": "Correction suggérée", "reason": "Pourquoi" }}
        ]
        Si aucune erreur, renvoie [].
        """

        suggestions = provider.generate_json(prompt, model_name=model_name)

        if not isinstance(suggestions, list):
            logger.warning(f"AI audit returned non-list: {type(suggestions)}")
            return []

        # Link back to transactions
        results = []
        for sugg in suggestions:
            if not isinstance(sugg, dict):
                continue

            clean_label_val = sugg.get("clean")
            current_cat = sugg.get("current")

            if not clean_label_val or not current_cat:
                continue

            # Find matching rows
            matches = df[
                (df["clean"] == clean_label_val) & (df["category_validated"] == current_cat)
            ]

            if not matches.empty:
                results.append(
                    {
                        "type": "Suspicion IA",
                        "label": clean_label_val,
                        "details": (
                            f"{current_cat} ➔ {sugg.get('suggested', '?')} "
                            f"({sugg.get('reason', 'Anomalie détectée')})"
                        ),
                        "suggested_category": sugg.get("suggested"),
                        "current_category": current_cat,
                        "reason": sugg.get("reason"),
                        "rows": matches,
                    }
                )

        return results

    except Exception as e:
        logger.error(f"Error in AI audit: {e}")
        return []


def run_full_audit(df: pd.DataFrame, use_ai: bool = True) -> dict[str, Any]:
    """
    Run complete audit with progress tracking.

    Args:
        df: DataFrame with transactions
        use_ai: Whether to include AI analysis

    Returns:
        Dictionary with audit results and metadata
    """
    results = {
        "inconsistencies": [],
        "ai_suggestions": [],
        "total_anomalies": 0,
        "completed": False,
        "error": None,
    }

    try:
        # Step 1: Detect inconsistencies
        results["inconsistencies"] = detect_inconsistencies(df)

        # Step 2: AI audit (if enabled)
        if use_ai:
            results["ai_suggestions"] = ai_audit_batch(df)

        results["total_anomalies"] = len(results["inconsistencies"]) + len(
            results["ai_suggestions"]
        )
        results["completed"] = True

    except Exception as e:
        logger.error(f"Audit failed: {e}")
        results["error"] = str(e)

    return results


def get_audit_summary(
    audit_results: list[dict], corrected: list[int], hidden: list[int]
) -> dict[str, int]:
    """
    Get summary statistics for audit results.

    Args:
        audit_results: List of all anomaly results
        corrected: Indices of corrected items
        hidden: Indices of hidden items

    Returns:
        Dictionary with counts
    """
    total = len(audit_results)
    corrected_count = len(corrected)
    hidden_count = len(hidden)

    # Count by type
    inconsistency_count = sum(1 for r in audit_results if r.get("type") == "Incohérence")
    ai_count = sum(1 for r in audit_results if r.get("type") == "Suspicion IA")

    return {
        "total": total,
        "corrected": corrected_count,
        "hidden": hidden_count,
        "pending": total - corrected_count - hidden_count,
        "inconsistencies": inconsistency_count,
        "ai_suggestions": ai_count,
    }
