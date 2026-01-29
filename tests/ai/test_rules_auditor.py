import pytest
import pandas as pd
from modules.ai.rules_auditor import analyze_rules_integrity

class TestRulesAuditor:
    def test_analyze_empty_rules(self):
        """Test auditing an empty dataframe."""
        df = pd.DataFrame(columns=['id', 'pattern', 'category', 'priority'])
        issues = analyze_rules_integrity(df)
        assert issues['conflicts'] == []
        assert issues['duplicates'] == []

    def test_detect_conflicts(self):
        """Test detecting same pattern with different categories."""
        df = pd.DataFrame([
            {'id': 1, 'pattern': 'TEST', 'category': 'Cat1', 'priority': 1},
            {'id': 2, 'pattern': 'TEST', 'category': 'Cat2', 'priority': 1},
        ])
        issues = analyze_rules_integrity(df)
        assert len(issues['conflicts']) == 1
        assert issues['conflicts'][0]['pattern'].upper() == 'TEST'

    def test_detect_duplicates(self):
        """Test detecting exact duplicates (same pattern/category)."""
        df = pd.DataFrame([
            {'id': 1, 'pattern': 'DUPE', 'category': 'Cat1', 'priority': 1},
            {'id': 2, 'pattern': 'dUpe', 'category': 'Cat1', 'priority': 1},
        ])
        issues = analyze_rules_integrity(df)
        assert len(issues['duplicates']) == 1
        assert issues['duplicates'][0]['pattern'].lower() == 'dupe'

    def test_detect_overlaps(self):
        """Test detecting overlapping patterns."""
        df = pd.DataFrame([
            {'id': 1, 'pattern': 'UBER', 'category': 'Transport', 'priority': 1},
            {'id': 2, 'pattern': 'UBER EATS', 'category': 'Food', 'priority': 1},
        ])
        issues = analyze_rules_integrity(df)
        assert len(issues['overlaps']) == 1
        assert issues['overlaps'][0]['shorter_pattern'] == 'UBER'

    def test_detect_vague(self):
        """Test detecting vague (short) patterns."""
        df = pd.DataFrame([
            {'id': 1, 'pattern': 'A', 'category': 'Cat1', 'priority': 1},
        ])
        issues = analyze_rules_integrity(df)
        assert len(issues['vague']) == 1
