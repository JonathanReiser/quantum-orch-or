import pytest
from q_ai_twitter_bot import QAITwitterBot

def test_q_ai_twitter_bot_cards():
    bot = QAITwitterBot()
    cards = bot.generate_tweet_cards()
    
    assert len(cards) > 0
    assert len(cards[0]) <= 280
    assert "Q-AI ORACLE FORECAST" in cards[0]
    assert "Vote Approval" in cards[0]

def test_q_ai_twitter_bot_cli_command(monkeypatch, capsys):
    from q_ai_governance.cli import main
    monkeypatch.setattr("sys.argv", ["q-ai-gov", "tweet", "--simulate"])
    main()
    
    captured = capsys.readouterr()
    assert "Twitter/X Q-AI Forecast Cards" in captured.out
