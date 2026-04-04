import pytest
import json
from ai_orchestrator import AIAgent
from services.quant_service import QuantService

def test_ai_thinking_trace_retention(mocker):
    """
    TDD: Verify that the AIAgent retains the <|thought|> channel in its output.
    Uses mocking for CI/CD environments where Ollama isn't local.
    """
    mock_ollama = mocker.patch("ollama.Client")
    mock_response = {
        'message': {
            'content': "<|thought|>Scenario analysis: Coors field + high humidity.<channel|>I recommend a bet on the Over."
        }
    }
    mock_ollama.return_value.chat.return_value = mock_response

    agent = AIAgent()
    state = {"inning": 8, "score_diff": 0}
    insight = agent.generate_insight("Test Rule", state)
    
    assert isinstance(insight, str)
    assert "<|thought|>" in insight
    assert "I recommend a bet on the Over" in insight

def test_clv_calculation_logic():
    """
    TDD: Verify that the system can calculate Closing Line Value (CLV).
    CLV = (Implied Prob at Closing) - (Implied Prob at Time of Bet)
    """
    # Mock implementation of CLV calculation in QuantService
    qs = QuantService()
    
    odds_taken = -110 # 52.38% implied
    odds_closing = -150 # 60.00% implied
    
    # Expected Edge: 60.00 - 52.38 = +7.62%
    clv = qs.calculate_clv(odds_taken, odds_closing)
    
    assert clv > 0
    assert pytest.approx(clv, 0.01) == 0.0762

def test_bet_logging_with_trace_and_clv(mocker):
    """
    TDD: Verify that the log_bet function correctly handles the new schema fields.
    """
    mock_db = mocker.patch("engine.get_db_connection")
    from engine import log_bet
    
    # This should now succeed with the mock
    log_bet(
        game_id=999999,
        system="TDD_TEST",
        odds=-110,
        stake=10.0,
        ai_insight="BET!",
        clv=0.05,
        ai_trace="<|thought|>I think this is good."
    )
    
    # Verify the SQL call includes the new fields
    args, _ = mock_db.return_value.cursor.return_value.execute.call_args
    sql = args[0]
    assert "clv" in sql
    assert "ai_trace" in sql
