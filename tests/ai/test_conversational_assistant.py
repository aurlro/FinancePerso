import pytest
from unittest.mock import MagicMock, patch
from modules.ai.conversational_assistant import chat_with_assistant

class TestConversationalAssistant:
    @patch('modules.ai.conversational_assistant.get_ai_provider')
    @patch('modules.ai.conversational_assistant.get_active_model_name')
    @patch('modules.ai.conversational_assistant.get_all_transactions')  # Mock DB
    @patch('modules.ai.conversational_assistant.get_categories')
    def test_chat_tool_call(self, mock_cats, mock_tx, mock_model, mock_provider):
        # Setup
        mock_cats.return_value = ["Alimentation", "Loisirs"]
        mock_model.return_value = "dummy-model"
        
        # Mock provider response with a tool call JSON
        mock_ai = MagicMock()
        tool_call_json = '{"tool": "get_budget_status", "kwargs": {"category": "Loisirs"}}'
        final_response = "Votre budget Loisirs est OK."
        
        # First call returns tool call, second call returns final answer
        mock_ai.generate_text.side_effect = [tool_call_json, final_response]
        mock_provider.return_value = mock_ai
        
        # We also need to mock execute_tool_call to simplify
        with patch('modules.ai.conversational_assistant.execute_tool_call') as mock_exec:
            mock_exec.return_value = {"status": "ok", "budget": 500}
            
            response = chat_with_assistant("Budget Loisirs ?")
            
            assert response == final_response
            assert mock_exec.called
            assert mock_exec.call_args[0][0] == "get_budget_status"
