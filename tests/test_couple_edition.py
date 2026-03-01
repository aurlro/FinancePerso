"""Tests pour la Couple Edition.

Teste les fonctionnalités de confidentialité et de gestion couple.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from modules.couple.card_mappings import (
    save_card_mapping,
    get_card_mapping,
    get_all_card_mappings,
    get_unknown_cards,
)
from modules.couple.couple_settings import (
    get_couple_settings,
    save_couple_settings,
    set_current_user,
    get_current_user_role,
    is_couple_configured,
    get_setup_progress,
)
from modules.couple.transfer_detector import detect_internal_transfers
from modules.couple.privacy_filters import (
    get_transaction_visibility_role,
    COUPLE_PRIVACY_RULES,
)
from modules.db.members import add_member, delete_member, get_members


class TestCoupleSettings:
    """Test la configuration couple."""
    
    def test_get_couple_settings_returns_defaults(self, temp_db):
        """La configuration par défaut doit être retournée."""
        settings = get_couple_settings()
        assert settings is not None
        assert 'member_a_id' in settings
        assert 'member_b_id' in settings
    
    def test_save_and_retrieve_settings(self, temp_db):
        """Doit pouvoir sauvegarder et récupérer les paramètres."""
        # Créer des membres de test
        add_member("TestA", "HOUSEHOLD")
        add_member("TestB", "HOUSEHOLD")
        
        # Récupérer les IDs (get_members retourne un DataFrame)
        members = get_members()
        member_a_id = int(members[members['name'] == "TestA"].iloc[0]['id'])
        member_b_id = int(members[members['name'] == "TestB"].iloc[0]['id'])
        
        # Sauvegarder
        result = save_couple_settings(
            member_a_id=member_a_id,
            member_b_id=member_b_id,
            current_user_id=member_a_id,
            joint_account_labels=["COMPTE JOINT", "LIVRET"]
        )
        assert result is True
        
        # Vérifier
        settings = get_couple_settings()
        assert settings['member_a_id'] == member_a_id
        assert settings['member_b_id'] == member_b_id
        assert settings['current_user_id'] == member_a_id
        assert "COMPTE JOINT" in settings['joint_account_labels']
        
        # Cleanup
        delete_member(member_a_id)
        delete_member(member_b_id)
    
    def test_is_couple_configured(self, temp_db):
        """Doit détecter quand la configuration est complète."""
        # Au début : non configuré
        assert is_couple_configured() is False
        
        # Créer des membres
        add_member("TestA", "HOUSEHOLD")
        add_member("TestB", "HOUSEHOLD")
        
        # Récupérer les IDs (get_members retourne un DataFrame)
        members = get_members()
        member_a_id = int(members[members['name'] == "TestA"].iloc[0]['id'])
        member_b_id = int(members[members['name'] == "TestB"].iloc[0]['id'])
        
        # Configurer partiellement
        save_couple_settings(member_a_id=member_a_id)
        assert is_couple_configured() is False  # Manque membre_b et current_user
        
        # Configurer complètement
        save_couple_settings(
            member_a_id=member_a_id,
            member_b_id=member_b_id,
            current_user_id=member_a_id
        )
        assert is_couple_configured() is True
        
        # Cleanup
        delete_member(member_a_id)
        delete_member(member_b_id)


class TestCardMappings:
    """Test le mapping des cartes."""
    
    def test_save_and_get_card_mapping(self, temp_db):
        """Doit pouvoir sauvegarder et récupérer un mapping."""
        # Sauvegarder
        result = save_card_mapping(
            card_suffix="1234",
            account_type="PERSONAL_A",
            label="Ma carte"
        )
        assert result is True
        
        # Récupérer
        mapping = get_card_mapping("1234")
        assert mapping is not None
        assert mapping['card_suffix'] == "1234"
        assert mapping['account_type'] == "PERSONAL_A"
        assert mapping['label'] == "Ma carte"
    
    def test_update_existing_mapping(self, temp_db):
        """Doit pouvoir mettre à jour un mapping existant."""
        # Créer
        save_card_mapping("5678", "UNKNOWN", label="Ancien")
        
        # Mettre à jour
        save_card_mapping("5678", "JOINT", label="Nouveau")
        
        # Vérifier
        mapping = get_card_mapping("5678")
        assert mapping['account_type'] == "JOINT"
        assert mapping['label'] == "Nouveau"
    
    def test_get_all_mappings(self, temp_db):
        """Doit retourner tous les mappings."""
        # Créer plusieurs
        save_card_mapping("1111", "PERSONAL_A")
        save_card_mapping("2222", "PERSONAL_B")
        save_card_mapping("3333", "JOINT")
        
        mappings = get_all_card_mappings()
        suffixes = [m['card_suffix'] for m in mappings]
        
        assert "1111" in suffixes
        assert "2222" in suffixes
        assert "3333" in suffixes


class TestPrivacyRules:
    """Test les règles de confidentialité."""
    
    def test_privacy_rules_structure(self):
        """Les règles doivent avoir la bonne structure."""
        for role in ['ME', 'PARTNER', 'JOINT', 'UNKNOWN']:
            assert role in COUPLE_PRIVACY_RULES
            rules = COUPLE_PRIVACY_RULES[role]
            assert 'can_see_details' in rules
            assert 'can_see_transactions' in rules
            assert 'can_see_categories' in rules
    
    def test_partner_cannot_see_details(self):
        """Le partenaire ne doit pas voir les détails."""
        partner_rules = COUPLE_PRIVACY_RULES['PARTNER']
        assert partner_rules['can_see_details'] is False
        assert partner_rules['can_see_transactions'] is False
        assert partner_rules['can_see_labels'] is False
    
    def test_me_can_see_everything(self):
        """L'utilisateur courant doit tout voir."""
        me_rules = COUPLE_PRIVACY_RULES['ME']
        assert me_rules['can_see_details'] is True
        assert me_rules['can_see_transactions'] is True
        assert me_rules['can_see_labels'] is True


class TestSetupProgress:
    """Test le calcul de progression."""
    
    def test_setup_progress_initial(self, temp_db):
        """Au départ, la progression doit être faible."""
        progress = get_setup_progress()
        
        assert 'steps' in progress
        assert 'percentage' in progress
        assert 'is_complete' in progress
        
        # Au début, pas complet
        assert progress['is_complete'] is False
        assert progress['percentage'] < 100
    
    def test_setup_progress_complete(self, temp_db):
        """Avec tout configuré, la progression doit être 100%."""
        # Créer membres
        add_member("TestA", "HOUSEHOLD")
        add_member("TestB", "HOUSEHOLD")
        
        # Récupérer les IDs (get_members retourne un DataFrame)
        members = get_members()
        member_a_id = int(members[members['name'] == "TestA"].iloc[0]['id'])
        member_b_id = int(members[members['name'] == "TestB"].iloc[0]['id'])
        
        # Configurer
        save_couple_settings(
            member_a_id=member_a_id,
            member_b_id=member_b_id,
            current_user_id=member_a_id,
            joint_account_labels=["JOINT"]
        )
        
        # Mapper une carte
        save_card_mapping("9999", "JOINT")
        
        # Vérifier progression
        progress = get_setup_progress()
        assert progress['is_complete'] is True
        assert progress['percentage'] == 100
        
        # Cleanup
        delete_member(member_a_id)
        delete_member(member_b_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
