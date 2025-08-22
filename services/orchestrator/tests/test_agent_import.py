def test_build_agent_imports():
    from app.agent import build_agent
    assert callable(build_agent)
