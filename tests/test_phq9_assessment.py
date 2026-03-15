"""
Tests for PHQ-9 Depression Assessment model.
"""

import pytest
from pydantic import ValidationError

from app.models.phq9 import PHQ9Assessment, SeverityLevel


class TestPHQ9AssessmentValidation:
    """Test data validation and constraints."""

    def test_valid_assessment_creation(self):
        """Should create assessment with valid scores."""
        assessment = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=2,
            q3_problemas_sono=1,
            q4_sentir_cansado=2,
            q5_comida=1,
            q6_fracasso=1,
            q7_concentracao=2,
            q8_inquietude=1,
            q9_pen_suicida=0,
        )
        assert assessment is not None
        assert isinstance(assessment, PHQ9Assessment)

    def test_score_below_minimum_raises_error(self):
        """Should reject scores below 0."""
        with pytest.raises(ValidationError) as exc_info:
            PHQ9Assessment(
                q1_interest=-1,  # Invalid
                q2_desanimado=2,
                q3_problemas_sono=1,
                q4_sentir_cansado=2,
                q5_comida=1,
                q6_fracasso=1,
                q7_concentracao=2,
                q8_inquietude=1,
                q9_pen_suicida=0,
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_score_above_maximum_raises_error(self):
        """Should reject scores above 3."""
        with pytest.raises(ValidationError) as exc_info:
            PHQ9Assessment(
                q1_interest=1,
                q2_desanimado=4,  # Invalid
                q3_problemas_sono=1,
                q4_sentir_cansado=2,
                q5_comida=1,
                q6_fracasso=1,
                q7_concentracao=2,
                q8_inquietude=1,
                q9_pen_suicida=0,
            )
        assert "less than or equal to 3" in str(exc_info.value)

    def test_missing_required_field_raises_error(self):
        """Should reject assessment with missing fields."""
        with pytest.raises(ValidationError) as exc_info:
            PHQ9Assessment(
                q1_interest=1,
                q2_desanimado=2,
                # Missing q3_problemas_sono
                q4_sentir_cansado=2,
                q5_comida=1,
                q6_fracasso=1,
                q7_concentracao=2,
                q8_inquietude=1,
                q9_pen_suicida=0,
            )
        assert "Field required" in str(exc_info.value)


class TestPHQ9Scoring:
    """Test score calculation logic."""

    def test_total_score_calculation(self):
        """Should correctly sum all question scores."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=3,
            q3_problemas_sono=2,
            q4_sentir_cansado=3,
            q5_comida=1,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=1,
            q9_pen_suicida=2,
        )
        assert assessment.total_score == 18

    def test_minimum_score(self):
        """Should calculate score of 0 for all zeros."""
        assessment = PHQ9Assessment(
            q1_interest=0,
            q2_desanimado=0,
            q3_problemas_sono=0,
            q4_sentir_cansado=0,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert assessment.total_score == 0

    def test_maximum_score(self):
        """Should calculate maximum score of 27."""
        assessment = PHQ9Assessment(
            q1_interest=3,
            q2_desanimado=3,
            q3_problemas_sono=3,
            q4_sentir_cansado=3,
            q5_comida=3,
            q6_fracasso=3,
            q7_concentracao=3,
            q8_inquietude=3,
            q9_pen_suicida=3,
        )
        assert assessment.total_score == 27


class TestPHQ9SeverityLevels:
    """Test severity classification."""

    def test_severity_none_minimal(self):
        """Score 0-4 should indicate no/minimal depression."""
        assessment = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert assessment.total_score == 4
        assert assessment.get_severity_level == SeverityLevel.NONE

    def test_severity_low_mild(self):
        """Score 5-9 should indicate mild depression."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=1,
            q4_sentir_cansado=2,
            q5_comida=1,
            q6_fracasso=1,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert assessment.total_score == 9
        assert assessment.get_severity_level == SeverityLevel.LOW

    def test_severity_moderate(self):
        """Score 10-14 should indicate moderate depression."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=2,
            q4_sentir_cansado=2,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=1,
            q8_inquietude=1,
            q9_pen_suicida=0,
        )
        assert assessment.total_score == 14
        assert assessment.get_severity_level == SeverityLevel.MODERATE

    def test_severity_high_moderately_severe(self):
        """Score 15-19 should indicate moderately severe depression."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=3,
            q3_problemas_sono=2,
            q4_sentir_cansado=3,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=1,
            q9_pen_suicida=2,
        )
        assert assessment.total_score == 19
        assert assessment.get_severity_level == SeverityLevel.HIGH

    def test_severity_severe(self):
        """Score 20-27 should indicate severe depression."""
        assessment = PHQ9Assessment(
            q1_interest=3,
            q2_desanimado=3,
            q3_problemas_sono=3,
            q4_sentir_cansado=3,
            q5_comida=3,
            q6_fracasso=2,
            q7_concentracao=3,
            q8_inquietude=2,
            q9_pen_suicida=3,
        )
        assert assessment.total_score == 25
        assert assessment.get_severity_level == SeverityLevel.SEVERE

    def test_severity_boundary_cases(self):
        """Test scores at severity boundaries."""
        # Boundary: 4 -> NONE, 5 -> LOW
        none_max = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert none_max.total_score == 4
        assert none_max.get_severity_level == SeverityLevel.NONE

        low_min = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=1,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert low_min.total_score == 5
        assert low_min.get_severity_level == SeverityLevel.LOW


class TestPHQ9CrisisDetection:
    """Test suicidal ideation detection."""

    def test_no_crisis_when_q9_zero(self):
        """Should not flag crisis when Q9 is 0."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=2,
            q4_sentir_cansado=2,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=2,
            q9_pen_suicida=0,
        )
        assert assessment.has_crisis_indicator is False

    def test_crisis_when_q9_is_one(self):
        """Should flag crisis when Q9 is 1 (several days)."""
        assessment = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=1,
            q6_fracasso=1,
            q7_concentracao=1,
            q8_inquietude=1,
            q9_pen_suicida=1,
        )
        assert assessment.has_crisis_indicator is True

    def test_crisis_when_q9_is_two(self):
        """Should flag crisis when Q9 is 2 (more than half the days)."""
        assessment = PHQ9Assessment(
            q1_interest=0,
            q2_desanimado=0,
            q3_problemas_sono=0,
            q4_sentir_cansado=0,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=2,
        )
        assert assessment.has_crisis_indicator is True

    def test_crisis_when_q9_is_three(self):
        """Should flag crisis when Q9 is 3 (nearly every day)."""
        assessment = PHQ9Assessment(
            q1_interest=0,
            q2_desanimado=0,
            q3_problemas_sono=0,
            q4_sentir_cansado=0,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=3,
        )
        assert assessment.has_crisis_indicator is True


class TestPHQ9LLMContext:
    """Test LLM context generation."""

    def test_to_llm_context_structure(self):
        """Should return properly structured dict for LLM."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=3,
            q3_problemas_sono=2,
            q4_sentir_cansado=3,
            q5_comida=1,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=1,
            q9_pen_suicida=2,
        )
        context = assessment.to_llm_context()

        assert "assessment_type" in context
        assert "assessment_name" in context
        assert "language" in context
        assert "scores" in context
        assert "severity" in context
        assert "crisis_indicators" in context
        assert "symptom_profile" in context

    def test_llm_context_assessment_metadata(self):
        """Should include correct assessment metadata."""
        assessment = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=1,
            q6_fracasso=1,
            q7_concentracao=1,
            q8_inquietude=1,
            q9_pen_suicida=0,
        )
        context = assessment.to_llm_context()

        assert context["assessment_type"] == "PHQ-9"
        assert context["assessment_name"] == "Patient Health Questionnaire-9 (Depression)"
        assert context["language"] == "pt-br"

    def test_llm_context_scores(self):
        """Should include correct score information."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=2,
            q4_sentir_cansado=2,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=2,
            q9_pen_suicida=2,
        )
        context = assessment.to_llm_context()

        assert context["scores"]["total"] == 18
        assert context["scores"]["max_possible"] == 27
        assert context["scores"]["percentage"] == 66.7

    def test_llm_context_severity(self):
        """Should include severity information."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=2,
            q4_sentir_cansado=2,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=1,
            q9_pen_suicida=1,
        )
        context = assessment.to_llm_context()

        assert context["severity"]["level"] == SeverityLevel.HIGH
        assert context["severity"]["clinical_range"] == "15-19"

    def test_llm_context_crisis_indicators(self):
        """Should include crisis detection information."""
        assessment = PHQ9Assessment(
            q1_interest=1,
            q2_desanimado=1,
            q3_problemas_sono=1,
            q4_sentir_cansado=1,
            q5_comida=1,
            q6_fracasso=1,
            q7_concentracao=1,
            q8_inquietude=1,
            q9_pen_suicida=2,
        )
        context = assessment.to_llm_context()

        assert context["crisis_indicators"]["has_crisis"] is True
        assert context["crisis_indicators"]["suicidal_ideation_score"] == 2
        assert context["crisis_indicators"]["requires_immediate_attention"] is True

    def test_llm_context_no_crisis(self):
        """Should correctly indicate no crisis when Q9 is 0."""
        assessment = PHQ9Assessment(
            q1_interest=2,
            q2_desanimado=2,
            q3_problemas_sono=2,
            q4_sentir_cansado=2,
            q5_comida=2,
            q6_fracasso=2,
            q7_concentracao=2,
            q8_inquietude=2,
            q9_pen_suicida=0,
        )
        context = assessment.to_llm_context()

        assert context["crisis_indicators"]["has_crisis"] is False
        assert context["crisis_indicators"]["requires_immediate_attention"] is False

    def test_llm_context_individual_scores(self):
        """Should include detailed individual question scores."""
        assessment = PHQ9Assessment(
            q1_interest=3,
            q2_desanimado=2,
            q3_problemas_sono=1,
            q4_sentir_cansado=2,
            q5_comida=1,
            q6_fracasso=2,
            q7_concentracao=1,
            q8_inquietude=1,
            q9_pen_suicida=0,
        )
        context = assessment.to_llm_context()
        individual = context["symptom_profile"]["individual_scores"]

        assert "interest_pleasure" in individual
        assert "depressed_mood" in individual
        assert "suicidal_ideation" in individual

        assert individual["interest_pleasure"]["score"] == 3
        assert individual["interest_pleasure"]["label"] == "Perda de interesse ou prazer"
        assert individual["interest_pleasure"]["clinical_term"] == "Anedonia"

        assert individual["suicidal_ideation"]["score"] == 0


class TestPHQ9EdgeCases:
    """Test edge cases and special scenarios."""

    def test_all_zeros_assessment(self):
        """Should handle assessment with all zero scores."""
        assessment = PHQ9Assessment(
            q1_interest=0,
            q2_desanimado=0,
            q3_problemas_sono=0,
            q4_sentir_cansado=0,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=0,
        )
        assert assessment.total_score == 0
        assert assessment.get_severity_level == SeverityLevel.NONE
        assert assessment.has_crisis_indicator is False

    def test_all_threes_assessment(self):
        """Should handle assessment with all maximum scores."""
        assessment = PHQ9Assessment(
            q1_interest=3,
            q2_desanimado=3,
            q3_problemas_sono=3,
            q4_sentir_cansado=3,
            q5_comida=3,
            q6_fracasso=3,
            q7_concentracao=3,
            q8_inquietude=3,
            q9_pen_suicida=3,
        )
        assert assessment.total_score == 27
        assert assessment.get_severity_level == SeverityLevel.SEVERE
        assert assessment.has_crisis_indicator is True

    def test_only_q9_endorsed(self):
        """Should flag crisis even if only Q9 is positive."""
        assessment = PHQ9Assessment(
            q1_interest=0,
            q2_desanimado=0,
            q3_problemas_sono=0,
            q4_sentir_cansado=0,
            q5_comida=0,
            q6_fracasso=0,
            q7_concentracao=0,
            q8_inquietude=0,
            q9_pen_suicida=1,
        )
        assert assessment.total_score == 1
        assert assessment.get_severity_level == SeverityLevel.NONE
        assert assessment.has_crisis_indicator is True
