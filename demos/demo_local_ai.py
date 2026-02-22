#!/usr/bin/env python3
"""
Démonstration IA Locale Souveraine
===================================

Script de démonstration pour tester la cascade de confiance
avec modèle local Llama 3.2.

Usage:
    python demo_local_ai.py

Requirements:
    pip install unsloth torch transformers
"""

import os
import sys
import time

# Configuration
os.environ["AI_PROVIDER"] = "local"
os.environ["LOCAL_SLM_FALLBACK"] = "false"  # Force local only for demo

def demo_heuristic():
    """Démo de la catégorisation par heuristique."""
    print("\n" + "="*60)
    print("🧮 ÉTAPE 1: RÈGLES HEURISTIQUES")
    print("="*60)
    
    from modules.categorization_cascade import TransactionCategorizer
    
    categorizer = TransactionCategorizer(use_local_ai=False, use_cloud_fallback=False)
    
    test_cases = [
        ("CARREFOUR PARIS 15", -45.67),
        ("MCDONALD'S PARIS", -12.50),
        ("TOTAL ENERGIES PARIS", -65.00),
        ("STARBUCKS PARIS 8", -6.50),
    ]
    
    for label, amount in test_cases:
        result = categorizer._check_heuristics(label, amount)
        if result:
            print(f"\n✅ {label}")
            print(f"   Catégorie: {result.category}")
            print(f"   Confiance: {result.confidence_score}")
            print(f"   Source: {result.source}")


def demo_similarity():
    """Démo de la similarité avec historique."""
    print("\n" + "="*60)
    print("🔍 ÉTAPE 2: SIMILARITÉ (SequenceMatcher)")
    print("="*60)
    
    from difflib import SequenceMatcher
    
    # Simuler l'historique
    history = [
        "CARREFOUR PARIS 15",
        "UBER EATS PARIS",
        "STARBUCKS RIVOLI",
    ]
    
    test_cases = [
        "CARREFOUR PARIS 16",  # Très similaire
        "CARREFOUR LYON",       # Similaire
        "RESTAURANT PIZZA",     # Différent
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: '{test}'")
        for hist in history:
            score = SequenceMatcher(None, test.upper(), hist.upper()).ratio()
            status = "✅ MATCH" if score >= 0.85 else "❌"
            print(f"   vs '{hist}': {score:.3f} {status}")


def demo_local_model():
    """Démo du modèle local (si disponible)."""
    print("\n" + "="*60)
    print("🤖 ÉTAPE 3: IA LOCALE (Llama 3.2 3B)")
    print("="*60)
    
    try:
        from modules.ai.local_slm_provider import get_local_slm_provider
        
        print("\n⏳ Chargement du modèle (peut prendre 30-60s)...")
        provider = get_local_slm_provider(
            model_name="llama-3.2-3b",
            fallback_to_cloud=False
        )
        
        info = provider.get_model_info()
        print(f"\n✅ Modèle chargé: {info['model_name']}")
        print(f"   VRAM utilisée: {info.get('vram_allocated_gb', 'N/A')} GB")
        print(f"   Quantification: {info['quantization']}")
        
        # Test de génération
        prompt = """Analyse cette transaction:
- Libellé: "PHARMACIE DU COIN PARIS"
- Montant: -23.50 EUR

Réponds avec ce JSON:
{
    "category": "Main > Sub",
    "clean_merchant": "string",
    "confidence_score": float
}"""
        
        print("\n⏳ Génération en cours...")
        start = time.time()
        result = provider.generate_json(prompt, temperature=0.1)
        elapsed = time.time() - start
        
        print(f"\n✅ Résultat ({elapsed:.2f}s):")
        print(f"   {result}")
        
    except ImportError as e:
        print(f"\n❌ Dépendances manquantes: {e}")
        print("   Installez avec: pip install unsloth torch transformers")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


def demo_full_cascade():
    """Démo complète de la cascade."""
    print("\n" + "="*60)
    print("🎯 CASCADE COMPLÈTE (1→2→3)")
    print("="*60)
    
    from modules.categorization_cascade import TransactionCategorizer
    
    categorizer = TransactionCategorizer(
        use_local_ai=True,
        use_cloud_fallback=False  # Skip cloud for demo
    )
    
    transactions = [
        ("CARREFOUR PARIS 15", -45.67),           # → Heuristique
        ("TOTAL ENERGIES PARIS", -60.00),         # → Heuristique
        ("RESTAURANT LE BISTROT PARIS", -35.00),  # → Similarité ou IA
        ("UNKNOWN MERCHANT XYZ123", -12.50),      # → IA
    ]
    
    for label, amount in transactions:
        print(f"\n📝 '{label}' ({amount:.2f}€)")
        
        # Forcer chaque étape pour la démo
        result = categorizer._check_heuristics(label, amount)
        if result:
            print(f"   ✅ HEURISTIQUE: {result.category}")
            continue
        
        result = categorizer._check_similarity(label)
        if result:
            print(f"   ✅ SIMILARITÉ: {result.category} (score: {result.similarity_score:.3f})")
            continue
        
        print(f"   🤖 IA: (nécessite modèle chargé)")


def main():
    """Point d'entrée principal."""
    print("\n" + "="*60)
    print("  🤖 DÉMO: IA LOCALE SOUVERAINE")
    print("  FinancePerso - Llama 3.2 3B Instruct")
    print("="*60)
    
    print("\n📋 Menu:")
    print("   1. Règles heuristiques")
    print("   2. Similarité (SequenceMatcher)")
    print("   3. Modèle local (si disponible)")
    print("   4. Cascade complète")
    print("   5. Toutes les démos")
    
    choice = input("\n➤ Votre choix (1-5): ").strip()
    
    if choice == "1":
        demo_heuristic()
    elif choice == "2":
        demo_similarity()
    elif choice == "3":
        demo_local_model()
    elif choice == "4":
        demo_full_cascade()
    elif choice == "5":
        demo_heuristic()
        demo_similarity()
        demo_local_model()
        demo_full_cascade()
    else:
        print("\n❌ Choix invalide")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ DÉMO TERMINÉE")
    print("="*60)


if __name__ == "__main__":
    main()
