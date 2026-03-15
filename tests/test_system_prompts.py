"""
Tests for system prompt generation.
"""

from app.utils.prompts.system_prompt import CustomSystemPrompts, prompts


class TestCustomSystemPrompts:
    """Test suite for system prompt generation."""

    def test_free_chat_prompt_not_empty(self):
        prompt = prompts.system_prompt_free_chat()
        assert prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 10

    def test_forms_chat_with_forms_prompt_not_empty(self):
        prompt = prompts.system_prompt_chat_with_forms()
        assert prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 10

    def test_forms_crisis_intervention_prompt_not_empty(self):
        prompt = prompts.system_prompt_chat_with_forms()
        assert prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 10

    def test_free_chat_contains_safety_guidelines(self):
        prompt = prompts.system_prompt_free_chat()
        assert "not a therapist" in prompt.lower()
        assert "professional" in prompt.lower()
        assert "crisis" in prompt.lower() or "severe" in prompt.lower()

    def test_crisis_intervention_contains_resources(self):
        addendum = prompts.system_prompt_crisis_intervention()
        assert "188" in addendum
        assert "CVV" in addendum
        assert "safe" in addendum.lower()

    def test_singleton_instance_available(self):
        assert prompts is not None
        assert isinstance(prompts, CustomSystemPrompts)

    def test_singleton_methods_accessible(self):
        assert callable(prompts.system_prompt_free_chat)
        assert callable(prompts.system_prompt_chat_with_forms)
        assert callable(prompts.system_prompt_crisis_intervention)
