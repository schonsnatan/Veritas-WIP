"""
Tests for GAD-7 Anxiety Assessment model.
"""

import pytest
from pydantic import ValidationError

from app.models.gad7 import GAD7Assessment, SeverityLevel


class TestGAD7Validation:
    """Test data validation."""

    def test_valid_assessment_creation(self):
        """Should create assessment with valid scores."""
        assessment = GAD7Assessment(
            q1_nervous=1,
            q2_stop_worrying=2,
            q3_worrying_too_much=1,
            q4_relaxing=2,
            q5_restless=1,
            q6_annoyed=1,
            q7_afraid=0,
        )
        assert assessment is not None

    def test_score_validation_fails(self):
        """Should reject invalid scores."""
        with pytest.raises(ValidationError):
            GAD7Assessment(
                q1_nervous=-1,  # Invalid
                q2_stop_worrying=2,
                q3_worrying_too_much=1,
                q4_relaxing=2,
                q5_restless=1,
                q6_annoyed=1,
                q7_afraid=0,
            )


class TestGAD7Scoring:
    """Test score calculation."""

    def test_total_score_calculation(self):
        """Should correctly sum all scores."""
        assessment = GAD7Assessment(
            q1_nervous=2,
            q2_stop_worrying=3,
            q3_worrying_too_much=2,
            q4_relaxing=3,
            q5_restless=1,
            q6_annoyed=2,
            q7_afraid=2,
        )
        assert assessment.total_score == 15

    def test_minimum_score(self):
        """Should calculate score of 0."""
        assessment = GAD7Assessment(
            q1_nervous=0,
            q2_stop_worrying=0,
            q3_worrying_too_much=0,
            q4_relaxing=0,
            q5_restless=0,
            q6_annoyed=0,
            q7_afraid=0,
        )
        assert assessment.total_score == 0

    def test_maximum_score(self):
        """Should calculate maximum score of 21."""
        assessment = GAD7Assessment(
            q1_nervous=3,
            q2_stop_worrying=3,
            q3_worrying_too_much=3,
            q4_relaxing=3,
            q5_restless=3,
            q6_annoyed=3,
            q7_afraid=3,
        )
        assert assessment.total_score == 21


class TestGAD7Severity:
    """Test severity classification."""

    def test_severity_minimal(self):
        """Score 0-4 should indicate minimal anxiety."""
        assessment = GAD7Assessment(
            q1_nervous=1,
            q2_stop_worrying=1,
            q3_worrying_too_much=1,
            q4_relaxing=1,
            q5_restless=0,
            q6_annoyed=0,
            q7_afraid=0,
        )
        assert assessment.total_score == 4
        assert assessment.get_severity_level == SeverityLevel.MINIMAL

    def test_severity_mild(self):
        """Score 5-9 should indicate mild anxiety."""
        assessment = GAD7Assessment(
            q1_nervous=2,
            q2_stop_worrying=2,
            q3_worrying_too_much=1,
            q4_relaxing=2,
            q5_restless=1,
            q6_annoyed=1,
            q7_afraid=0,
        )
        assert assessment.total_score == 9
        assert assessment.get_severity_level == SeverityLevel.MILD

    def test_severity_moderate(self):
        """Score 10-14 should indicate moderate anxiety."""
        assessment = GAD7Assessment(
            q1_nervous=2,
            q2_stop_worrying=2,
            q3_worrying_too_much=2,
            q4_relaxing=2,
            q5_restless=2,
            q6_annoyed=2,
            q7_afraid=2,
        )
        assert assessment.total_score == 14
        assert assessment.get_severity_level == SeverityLevel.MODERATE

    def test_severity_severe(self):
        """Score 15+ should indicate severe anxiety."""
        assessment = GAD7Assessment(
            q1_nervous=3,
            q2_stop_worrying=3,
            q3_worrying_too_much=3,
            q4_relaxing=3,
            q5_restless=3,
            q6_annoyed=0,
            q7_afraid=0,
        )
        assert assessment.total_score == 15
        assert assessment.get_severity_level == SeverityLevel.SEVERE


class TestGAD7CrisisIndicator:
    """Test crisis detection."""

    def test_no_crisis_indicator(self):
        """GAD-7 should never flag crisis (no suicidal ideation question)."""
        assessment = GAD7Assessment(
            q1_nervous=3,
            q2_stop_worrying=3,
            q3_worrying_too_much=3,
            q4_relaxing=3,
            q5_restless=3,
            q6_annoyed=3,
            q7_afraid=3,
        )
        assert assessment.has_crisis_indicator is False


class TestGAD7LLMContext:
    """Test LLM context generation."""

    def test_llm_context_structure(self):
        """Should return properly structured dict."""
        assessment = GAD7Assessment(
            q1_nervous=2,
            q2_stop_worrying=2,
            q3_worrying_too_much=2,
            q4_relaxing=2,
            q5_restless=2,
            q6_annoyed=2,
            q7_afraid=2,
        )
        context = assessment.to_llm_context()

        assert "assessment_type" in context
        assert "scores" in context
        assert "severity" in context
        assert "crisis_indicators" in context
        assert context["assessment_type"] == "GAD-7"

    def test_llm_context_max_score_21(self):
        """Should use max score of 21, not 27."""
        assessment = GAD7Assessment(
            q1_nervous=3,
            q2_stop_worrying=3,
            q3_worrying_too_much=3,
            q4_relaxing=3,
            q5_restless=3,
            q6_annoyed=3,
            q7_afraid=3,
        )
        context = assessment.to_llm_context()

        assert context["scores"]["max_possible"] == 21
        assert context["scores"]["total"] == 21
        assert context["scores"]["percentage"] == 100.0

    def test_llm_context_no_crisis(self):
        """Should indicate no crisis capability."""
        assessment = GAD7Assessment(
            q1_nervous=3,
            q2_stop_worrying=3,
            q3_worrying_too_much=3,
            q4_relaxing=3,
            q5_restless=3,
            q6_annoyed=3,
            q7_afraid=3,
        )
        context = assessment.to_llm_context()

        assert context["crisis_indicators"]["has_crisis"] is False
