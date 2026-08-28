import pytest
from q_ai_bot import QAIGovernanceBot

def test_q_ai_bot_alert_generation():
    bot = QAIGovernanceBot()
    alerts = bot.generate_alerts()
    
    assert len(alerts) > 0
    assert "Q-AI GOVERNANCE ALERT" in alerts[0]
    assert "Q-AI Oracle Vote Forecast" in alerts[0]

def test_q_ai_bot_telegram_dispatch():
    bot = QAIGovernanceBot()
    # Test with dummy token/chat_id to verify error handling without crashing
    count = bot.send_telegram_alert("INVALID_TOKEN", "123456789")
    assert count == 0

def test_q_ai_bot_cli_command(monkeypatch, capsys):
    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "bot", "--simulate"])
    main()
    
    captured = capsys.readouterr()
    assert "Q-AI Governance Alerts" in captured.out
