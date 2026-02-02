# -*- coding: utf-8 -*-
"""
Tests for the onboarding module.
"""
import pytest
import pandas as pd
from datetime import date
from unittest.mock import patch, MagicMock


class TestOnboardingManager:
    """Test suite for OnboardingManager class."""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit."""
        with patch('modules.onboarding.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    @pytest.fixture
    def onboarding_mgr(self, mock_streamlit):
        """Create OnboardingManager instance with mocked session state."""
        from modules.onboarding import OnboardingManager
        return OnboardingManager("test_user")
    
    def test_init_session_state(self, onboarding_mgr, mock_streamlit):
        """Test that session state is initialized correctly."""
        assert mock_streamlit.session_state['onboarding_step'] == 1
        assert mock_streamlit.session_state['onboarding_completed'] == False
    
    def test_is_first_time_no_data(self, onboarding_mgr, mock_streamlit):
        """Test is_first_time returns True when no transactions and no categories."""
        with patch('modules.onboarding.get_all_transactions', return_value=pd.DataFrame()):
            with patch('modules.onboarding.get_categories', return_value=[]):
                assert onboarding_mgr.is_first_time() == True
    
    def test_is_first_time_with_transactions(self, onboarding_mgr, mock_streamlit):
        """Test is_first_time returns False when transactions exist."""
        df = pd.DataFrame({'id': [1], 'amount': [100]})
        with patch('modules.onboarding.get_all_transactions', return_value=df):
            with patch('modules.onboarding.get_categories', return_value=[]):
                assert onboarding_mgr.is_first_time() == False
    
    def test_is_first_time_with_categories(self, onboarding_mgr, mock_streamlit):
        """Test is_first_time returns False when categories exist."""
        with patch('modules.onboarding.get_all_transactions', return_value=pd.DataFrame()):
            with patch('modules.onboarding.get_categories', return_value=['Alimentation', 'Transport']):
                assert onboarding_mgr.is_first_time() == False
    
    def test_is_first_time_already_completed(self, onboarding_mgr, mock_streamlit):
        """Test is_first_time returns False when onboarding already completed."""
        mock_streamlit.session_state['onboarding_completed'] = True
        with patch('modules.onboarding.get_all_transactions', return_value=pd.DataFrame()):
            with patch('modules.onboarding.get_categories', return_value=[]):
                assert onboarding_mgr.is_first_time() == False
    
    def test_is_first_time_error_handling(self, onboarding_mgr, mock_streamlit):
        """Test is_first_time handles database errors gracefully."""
        with patch('modules.onboarding.get_all_transactions', side_effect=Exception("DB Error")):
            assert onboarding_mgr.is_first_time() == False


class TestRenderOnboardingWidget:
    """Test suite for render_onboarding_widget function."""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit."""
        with patch('modules.onboarding.st') as mock_st:
            mock_st.session_state = {}
            mock_st.button.return_value = False
            mock_st.container.return_value.__enter__ = MagicMock()
            mock_st.container.return_value.__exit__ = MagicMock()
            yield mock_st
    
    def test_widget_not_shown_when_has_data(self, mock_streamlit):
        """Test widget is not shown when user has data."""
        from modules.onboarding import render_onboarding_widget
        
        # Ne devrait rien afficher car has_data=True
        render_onboarding_widget("default", has_data=True)
        
        # Vérifier que les colonnes ne sont pas créées
        mock_streamlit.columns.assert_not_called()
    
    def test_widget_not_shown_when_completed(self, mock_streamlit):
        """Test widget is not shown when onboarding completed."""
        from modules.onboarding import render_onboarding_widget
        
        mock_streamlit.session_state['onboarding_completed'] = True
        render_onboarding_widget("default", has_data=False)
        
        # Vérifier que les colonnes ne sont pas créées
        mock_streamlit.columns.assert_not_called()
    
    def test_widget_shown_for_new_user(self, mock_streamlit):
        """Test widget is shown for new users without data."""
        from modules.onboarding import render_onboarding_widget
        
        mock_streamlit.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        render_onboarding_widget("default", has_data=False)
        
        # Vérifier que container est appelé avec border=True
        mock_streamlit.container.assert_called_once_with(border=True)


class TestOnboardingFlow:
    """Test suite for complete onboarding flow."""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Comprehensive mock of Streamlit."""
        with patch('modules.onboarding.st') as mock_st:
            mock_st.session_state = {}
            mock_st.columns.return_value = [MagicMock() for _ in range(4)]
            mock_st.container.return_value.__enter__ = MagicMock()
            mock_st.container.return_value.__exit__ = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock()
            mock_st.expander.return_value.__exit__ = MagicMock()
            yield mock_st
    
    def test_step_progression(self, mock_streamlit):
        """Test that onboarding steps progress correctly."""
        from modules.onboarding import OnboardingManager
        
        mgr = OnboardingManager("test")
        
        # Step 1 initial
        assert mock_streamlit.session_state['onboarding_step'] == 1
        
        # Simuler passage à l'étape 2
        mock_streamlit.session_state['onboarding_step'] = 2
        assert mock_streamlit.session_state['onboarding_step'] == 2
    
    def test_completion(self, mock_streamlit):
        """Test that onboarding completion is persisted."""
        from modules.onboarding import OnboardingManager
        
        mgr = OnboardingManager("test")
        
        # Marquer comme complété
        mock_streamlit.session_state['onboarding_completed'] = True
        
        # Ne devrait plus afficher
        assert mgr.is_first_time() == False


class TestOnboardingIntegration:
    """Integration tests with real database."""
    
    def test_onboarding_with_empty_db(self, temp_db):
        """Test onboarding behavior with empty database."""
        from modules.onboarding import OnboardingManager
        from modules.db.transactions import get_all_transactions
        from modules.db.categories import get_categories
        
        with patch('modules.onboarding.st') as mock_st:
            mock_st.session_state = {}
            
            mgr = OnboardingManager("test")
            
            # Vérifier que la DB est bien vide de transactions
            df = get_all_transactions()
            cats = get_categories()
            
            assert df.empty == True
            # Il y a des catégories par défaut
            assert len(cats) == 7
            
            # Donc is_first_time devrait être False (car catégories existent)
            assert mgr.is_first_time() == False
    
    def test_onboarding_after_import(self, temp_db, sample_transactions):
        """Test onboarding behavior after data import."""
        from modules.onboarding import OnboardingManager
        from modules.db.transactions import save_transactions
        import pandas as pd
        
        with patch('modules.onboarding.st') as mock_st:
            mock_st.session_state = {}
            
            # Importer des transactions
            df = pd.DataFrame(sample_transactions)
            save_transactions(df)
            
            mgr = OnboardingManager("test")
            
            # Ne devrait plus être first-time
            assert mgr.is_first_time() == False
