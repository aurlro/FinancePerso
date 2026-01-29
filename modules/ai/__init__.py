"""
AI-powered features for financial analysis and assistance.

This module provides intelligent features including:
- Anomaly detection for unusual transaction amounts
- Smart tag suggestions based on context
- Trend analysis for spending patterns
- Conversational AI assistant
- Budget prediction and alerts
"""

from modules.ai.anomaly_detector import detect_amount_anomalies
from modules.ai.smart_tagger import suggest_tags_for_transaction, suggest_tags_batch
from modules.ai.budget_predictor import predict_budget_overruns, get_budget_alerts_summary
from modules.ai.trend_analyzer import analyze_spending_trends, get_top_categories_comparison
from modules.ai.conversational_assistant import chat_with_assistant

__all__ = [
    'detect_amount_anomalies',
    'suggest_tags_for_transaction',
    'suggest_tags_batch',
    'predict_budget_overruns',
    'get_budget_alerts_summary',
    'analyze_spending_trends',
    'get_top_categories_comparison',
    'chat_with_assistant',
]
