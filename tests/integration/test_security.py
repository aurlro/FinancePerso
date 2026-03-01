"""
Test Intégration: Sécurité et AML
==================================
"""

import pytest
from modules.wealth.security_monitor import SecurityMonitor, RiskLevel


class TestSecurity:
    """Tests de sécurité"""
    
    def test_aml_detection(self):
        """Test: Détection transaction suspecte"""
        monitor = SecurityMonitor()
        
        # Transaction suspecte
        suspicious_tx = {
            'id': 'tx-001',
            'amount': 50000,  # Montant élevé
            'date': '2026-02-21T03:00:00',  # Heure inhabituelle
            'label': 'CRYPTO EXCHANGE',
            'country_code': 'RU',  # Pays à risque
        }
        
        score = monitor.analyze_transaction(suspicious_tx)
        
        assert score.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        assert len(score.flags) > 0
        assert score.requires_review == True
    
    def test_normal_transaction(self):
        """Test: Transaction normale n'est pas flaggée"""
        monitor = SecurityMonitor()
        
        normal_tx = {
            'id': 'tx-002',
            'amount': 45.50,
            'date': '2026-02-18T14:30:00',  # Jour de semaine
            'label': 'SUPERMARCHE CARREFOUR',
        }
        
        score = monitor.analyze_transaction(normal_tx)
        
        # Une transaction normale peut avoir un faible risque (week-end, etc.)
        assert score.level in (RiskLevel.NONE, RiskLevel.LOW)
        assert score.score < 20  # Score faible
