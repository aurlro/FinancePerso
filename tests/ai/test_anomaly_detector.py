import pytest
import pandas as pd
from modules.ai.anomaly_detector import detect_amount_anomalies

class TestAnomalyDetector:
    def test_detect_anomaly_and_ignore(self):
        # Create data for a label 'SHOP'
        # 4 normal transactions (10€)
        # 1 anomaly (100€)
        data = [
            {'id': 1, 'date': '2024-01-01', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 2, 'date': '2024-01-02', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 3, 'date': '2024-01-03', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 4, 'date': '2024-01-04', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 5, 'date': '2024-01-05', 'label': 'SHOP', 'amount': -100.0, 'category_validated': 'Food', 'tags': ''},
        ]
        df = pd.DataFrame(data)
        
        # Should detect 1 anomaly (id 5)
        anomalies = detect_amount_anomalies(df, threshold_sigma=1.0)
        assert len(anomalies) == 1
        assert 5 in anomalies[0]['rows']['id'].values
        
        # Now mark as ignored
        df.loc[df['id'] == 5, 'tags'] = 'ignore_anomaly'
        
        # Should NOT detect any anomaly
        # (The only potential one is ignored, and the others are identical)
        anomalies_none = detect_amount_anomalies(df)
        assert len(anomalies_none) == 0

    def test_exclude_ignore_from_stats(self):
        # Even if a value is high, if it's ignored, it shouldn't bias the mean of others
        # (Though in our case, if ignored, it's just removed from df_exp)
        data = [
            {'id': 1, 'date': '2024-01-01', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 2, 'date': '2024-01-02', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 3, 'date': '2024-01-03', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 4, 'date': '2024-01-04', 'label': 'SHOP', 'amount': -10.0, 'category_validated': 'Food', 'tags': ''},
            {'id': 5, 'date': '2024-01-05', 'label': 'SHOP', 'amount': -100.0, 'category_validated': 'Food', 'tags': 'ignore_anomaly'},
            {'id': 6, 'date': '2024-01-06', 'label': 'SHOP', 'amount': -11.0, 'category_validated': 'Food', 'tags': ''},
        ]
        df = pd.DataFrame(data)
        
        # id 6 is not an anomaly compared to 10€, but would be if 100€ was included in mean
        # detect_amount_anomalies uses threshold_sigma=2.0
        anomalies = detect_amount_anomalies(df)
        assert len(anomalies) == 0 # 100 is ignored, others are close
