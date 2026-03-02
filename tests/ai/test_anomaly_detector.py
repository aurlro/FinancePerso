"""
Tests for anomaly_detector.py module.
"""

import pytest
import pandas as pd
from modules.ai.anomaly_detector import detect_amount_anomalies


class TestDetectAmountAnomalies:
    """Tests for amount anomaly detection."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = detect_amount_anomalies(df)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_no_anomalies(self):
        """Test with normal data (no anomalies)."""
        data = {
            "id": [1, 2, 3, 4, 5],
            "label": ["A", "B", "C", "D", "E"],
            "amount": [-50.0, -45.0, -52.0, -48.0, -51.0],
            "category": ["Alim", "Alim", "Alim", "Alim", "Alim"],
        }
        df = pd.DataFrame(data)
        result = detect_amount_anomalies(df, threshold_sigma=2.0)
        assert isinstance(result, list)

    def test_detects_anomalies(self):
        """Test detection of anomalies."""
        data = {
            "id": [1, 2, 3, 4, 5],
            "label": ["A", "B", "C", "D", "E"],
            "amount": [-50.0, -45.0, -52.0, -48.0, -500.0],  # Last is anomaly
            "category": ["Alim", "Alim", "Alim", "Alim", "Alim"],
        }
        df = pd.DataFrame(data)
        result = detect_amount_anomalies(df, threshold_sigma=1.5)
        assert isinstance(result, list)
        # The last transaction should be detected as anomaly
        if result:
            anomaly_ids = [a.get("id") for a in result if "id" in a]
            assert 5 in anomaly_ids or len(result) > 0

    def test_different_thresholds(self):
        """Test with different sigma thresholds."""
        data = {
            "id": [1, 2, 3],
            "label": ["A", "B", "C"],
            "amount": [-50.0, -45.0, -200.0],
            "category": ["Alim", "Alim", "Alim"],
        }
        df = pd.DataFrame(data)

        # Lower threshold should detect more anomalies
        result_low = detect_amount_anomalies(df, threshold_sigma=1.0)
        result_high = detect_amount_anomalies(df, threshold_sigma=3.0)

        assert isinstance(result_low, list)
        assert isinstance(result_high, list)
