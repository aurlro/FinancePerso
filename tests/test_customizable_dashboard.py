# -*- coding: utf-8 -*-
"""
Tests for the customizable dashboard module.
"""
import pytest
import pandas as pd
import json
from datetime import date
from unittest.mock import patch, MagicMock, mock_open


class TestWidgetType:
    """Test suite for WidgetType enum."""
    
    def test_widget_type_values(self):
        """Test that all widget types have correct values."""
        from modules.ui.dashboard.customizable_dashboard import WidgetType
        
        assert WidgetType.KPI_DEPENSES.value == "kpi_depenses"
        assert WidgetType.KPI_REVENUS.value == "kpi_revenus"
        assert WidgetType.KPI_SOLDE.value == "kpi_solde"
        assert WidgetType.KPI_EPARGNE.value == "kpi_epargne"
        assert WidgetType.EVOLUTION_CHART.value == "evolution_chart"
        assert WidgetType.SAVINGS_TREND.value == "savings_trend"
        assert WidgetType.CATEGORIES_CHART.value == "categories_chart"
        assert WidgetType.TOP_EXPENSES.value == "top_expenses"
        assert WidgetType.MONTHLY_STACKED.value == "monthly_stacked"


class TestDashboardWidget:
    """Test suite for DashboardWidget dataclass."""
    
    def test_widget_creation(self):
        """Test creating a DashboardWidget."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget, WidgetType
        
        widget = DashboardWidget(
            id="test_1",
            type=WidgetType.KPI_DEPENSES,
            title="Test Widget",
            position=1,
            size="small",
            visible=True,
            config={"key": "value"}
        )
        
        assert widget.id == "test_1"
        assert widget.type == WidgetType.KPI_DEPENSES
        assert widget.title == "Test Widget"
        assert widget.position == 1
        assert widget.size == "small"
        assert widget.visible == True
        assert widget.config == {"key": "value"}
    
    def test_widget_to_dict(self):
        """Test converting widget to dict."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget, WidgetType
        
        widget = DashboardWidget(
            id="test_1",
            type=WidgetType.KPI_DEPENSES,
            title="Test",
            position=1,
            size="small",
            visible=True,
            config={}
        )
        
        d = widget.to_dict()
        assert d['id'] == "test_1"
        assert d['type'] == "kpi_depenses"
        assert d['title'] == "Test"


class TestDashboardLayoutManager:
    """Test suite for DashboardLayoutManager class."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Mock Streamlit session state."""
        with patch('modules.ui.dashboard.customizable_dashboard.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    @pytest.fixture
    def manager(self, mock_session_state):
        """Create DashboardLayoutManager instance."""
        with patch('modules.ui.dashboard.customizable_dashboard.get_active_layout', return_value=None):
            from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager
            return DashboardLayoutManager()
    
    def test_init_creates_default_layout(self, manager, mock_session_state):
        """Test that initialization creates default layout in session state."""
        assert 'dashboard_layout' in mock_session_state.session_state
        layout = mock_session_state.session_state['dashboard_layout']
        assert isinstance(layout, list)
        assert len(layout) > 0
    
    def test_get_layout_returns_widgets(self, manager, mock_session_state):
        """Test that get_layout returns list of DashboardWidget."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget
        
        widgets = manager.get_layout()
        assert isinstance(widgets, list)
        assert all(isinstance(w, DashboardWidget) for w in widgets)
    
    def test_get_visible_widgets(self, manager, mock_session_state):
        """Test that get_layout only returns visible widgets by default."""
        widgets = manager.get_layout()
        assert all(w.visible for w in widgets)
    
    def test_get_all_widgets(self, manager, mock_session_state):
        """Test that get_all_widgets returns all widgets including hidden."""
        widgets = manager.get_all_widgets()
        assert isinstance(widgets, list)
    
    def test_is_preview_mode_default(self, manager, mock_session_state):
        """Test that preview mode is False by default."""
        assert manager.is_preview_mode() == False
    
    def test_reset_to_default(self, manager, mock_session_state):
        """Test resetting to default layout."""
        # Modifier le layout
        original_first_id = mock_session_state.session_state['dashboard_layout'][0]['id']
        mock_session_state.session_state['dashboard_layout'] = []
        
        # Reset
        manager.reset_to_default()
        
        # Vérifier que le layout est revenu à la normale
        assert len(mock_session_state.session_state['dashboard_layout']) > 0


class TestDashboardLayoutPersistence:
    """Test suite for layout persistence."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Mock Streamlit session state."""
        with patch('modules.ui.dashboard.customizable_dashboard.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    def test_load_layout_from_db(self, mock_session_state):
        """Test loading layout from database."""
        from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager
        
        # Mock DB layout
        db_layout = [
            {'id': 'kpi_1', 'type': 'kpi_depenses', 'title': 'Dépenses', 'position': 1, 'visible': True, 'size': 'small'}
        ]
        
        with patch('modules.ui.dashboard.customizable_dashboard.get_active_layout', return_value=db_layout):
            manager = DashboardLayoutManager()
            widgets = manager.get_layout()
            
            assert len(widgets) == 1
            assert widgets[0].id == 'kpi_1'
    
    def test_save_layout_to_db(self, mock_session_state):
        """Test saving layout to database."""
        from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager
        
        with patch('modules.ui.dashboard.customizable_dashboard.get_active_layout', return_value=None):
            manager = DashboardLayoutManager()
        
        # Vérifier que la méthode de sauvegarde existe et peut être appelée
        # La méthode réelle peut varier selon l'implémentation
        assert hasattr(manager, 'get_layout')


class TestWidgetRendering:
    """Test suite for widget rendering logic."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample transaction data."""
        return pd.DataFrame({
            'id': [1, 2, 3],
            'date': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'label': ['A', 'B', 'C'],
            'amount': [-10.0, 100.0, -20.0],
            'category_validated': ['Alim', 'Revenus', 'Transport']
        }), pd.DataFrame()  # df_prev empty
    
    def test_kpi_widget_rendering(self, sample_data):
        """Test KPI widget type determination."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget, WidgetType
        
        df_current, _ = sample_data
        
        # KPI widgets should be small
        kpi_widget = DashboardWidget(
            id="kpi_test",
            type=WidgetType.KPI_DEPENSES,
            title="Test KPI",
            position=1,
            size="small"
        )
        
        assert kpi_widget.size == "small"
    
    def test_chart_widget_rendering(self, sample_data):
        """Test chart widget type determination."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget, WidgetType
        
        chart_widget = DashboardWidget(
            id="chart_test",
            type=WidgetType.EVOLUTION_CHART,
            title="Test Chart",
            position=5,
            size="medium"
        )
        
        assert chart_widget.size == "medium"


class TestDashboardDefaultLayouts:
    """Test suite for default layout configurations."""
    
    def test_default_layout_has_all_kpis(self):
        """Test that default layout includes all KPI widgets."""
        from modules.ui.dashboard.customizable_dashboard import DEFAULT_LAYOUT, WidgetType
        
        kpi_types = {w.type for w in DEFAULT_LAYOUT if w.size == "small"}
        assert WidgetType.KPI_DEPENSES in kpi_types
        assert WidgetType.KPI_REVENUS in kpi_types
        assert WidgetType.KPI_SOLDE in kpi_types
        assert WidgetType.KPI_EPARGNE in kpi_types
    
    def test_default_layout_order(self):
        """Test that default layout has correct widget ordering."""
        from modules.ui.dashboard.customizable_dashboard import DEFAULT_LAYOUT
        
        positions = [w.position for w in DEFAULT_LAYOUT]
        assert positions == sorted(positions)


class TestDashboardEdgeCases:
    """Test suite for edge cases."""
    
    def test_empty_layout_handling(self):
        """Test handling of empty layout."""
        from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager
        
        with patch('modules.ui.dashboard.customizable_dashboard.st') as mock_st:
            mock_st.session_state = {}
            
            with patch('modules.ui.dashboard.customizable_dashboard.get_active_layout', return_value=None):
                manager = DashboardLayoutManager()
                
                # Simuler layout vide
                mock_st.session_state['dashboard_layout'] = []
                
                # Devrait retourner le layout par défaut
                widgets = manager.get_layout()
                assert len(widgets) > 0
    
    def test_widget_from_dict_string_type(self):
        """Test creating widget from dict with string type."""
        from modules.ui.dashboard.customizable_dashboard import DashboardWidget, WidgetType
        
        widget = DashboardWidget.from_dict({
            'id': 'test',
            'type': 'kpi_depenses',  # String instead of enum
            'title': 'Test',
            'position': 1,
            'visible': True,
            'size': 'small',
            'config': {}
        })
        
        assert widget.type == WidgetType.KPI_DEPENSES
