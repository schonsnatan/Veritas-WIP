from enum import Enum

from pydantic import BaseModel, Field

from app.models.base import BaseAssessment


class SeverityLevel(str, Enum):
    MINIMAL = "Ansiedade mínima"
    MILD = "Ansiedade Leve"
    MODERATE = " Ansiedade Moderada"
    SEVERE = "Ansiedade grave"


class GAD7Assessment(BaseModel, BaseAssessment):
    q1_nervous: int = Field(..., ge=0, le=3, description="Sentir-se nervoso, ansioso ou tenso")
    q2_stop_worrying: int = Field(..., ge=0, le=3, description="Não conseguir parar ou controlar a preocupação")
    q3_worrying_too_much: int = Field(..., ge=0, le=3, description="Preocupar-se demais com coisas diferentes.")
    q4_relaxing: int = Field(..., ge=0, le=3, description="Dificuldade em relaxar")
    q5_restless: int = Field(..., ge=0, le=3, description="Tão inquieto que é difícil ficar parado.")
    q6_annoyed: int = Field(..., ge=0, le=3, description="Ficar irritado ou aborrecido com facilidade")
    q7_afraid: int = Field(..., ge=0, le=3, description="Sentir medo, como se algo terrível pudesse acontecer.")

    @property
    def total_score(self):
        return sum(
            [
                self.q1_nervous,
                self.q2_stop_worrying,
                self.q3_worrying_too_much,
                self.q4_relaxing,
                self.q5_restless,
                self.q6_annoyed,
                self.q7_afraid,
            ]
        )

    @property
    def get_severity_level(self) -> SeverityLevel:
        score = self.total_score
        if score <= 4:
            return SeverityLevel.MINIMAL
        elif score <= 9:
            return SeverityLevel.MILD
        elif score <= 14:
            return SeverityLevel.MODERATE
        elif score >= 15:
            return SeverityLevel.SEVERE

    @property
    def has_crisis_indicator(self) -> bool:
        """GAD-7 does not include suicidal ideation screening"""
        return False

    def __get_severity_range(self) -> str:
        """Get the score range for current severity level"""
        ranges = {
            "MINIMAL": "0-4",
            "MILD": "5-9",
            "MODERATE": "10-14",
            "SEVERE": "15-21",
        }
        return ranges[self.get_severity_level.name]

    def __get_individual_scores(self) -> dict:
        """Get all question scores with labels"""
        return {
            "nervous_feeling": {
                "score": self.q1_nervous,
                "label": "Sentir-se nervoso, ansioso ou tenso",
                "clinical_term": "Tensão/Nervosismo",
            },
            "uncontrolled_worrying": {
                "score": self.q2_stop_worrying,
                "label": "Preocupação descontrolada",
                "clinical_term": "Preocupação incontrolável",
            },
            "excessive_worrying": {
                "score": self.q3_worrying_too_much,
                "label": "Preocupar-se constantemente",
                "clinical_term": "Preocupação excessiva",
            },
            "trouble_relaxing": {
                "score": self.q4_relaxing,
                "label": "Dificuldade em relaxar",
                "clinical_term": "Tensão muscular/mental",
            },
            "restlessness": {
                "score": self.q5_restless,
                "label": "Inquietude",
                "clinical_term": "Agitação psicomotora",
            },
            "irritability": {
                "score": self.q6_annoyed,
                "label": "Irritabilidade",
                "clinical_term": "Irritabilidade",
            },
            "fear": {
                "score": self.q7_afraid,
                "label": "Sentir medo",
                "clinical_term": "Ansiedade antecipatória",
            },
        }

    def to_llm_context(self) -> dict:
        return {
            "assessment_type": "GAD-7",
            "assessment_name": "Generalized Anxiety Disorder 7-item Assessment (Anxiety)",
            "language": "pt-br",
            "scores": {
                "total": self.total_score,
                "max_possible": 21,
                "percentage": round((self.total_score / 21) * 100, 1),
            },
            "severity": {
                "level": self.get_severity_level,
                "clinical_range": self.__get_severity_range(),
            },
            "crisis_indicators": {
                "has_crisis": False,
                "note": "GAD-7 does not screen for suicidal ideation",
            },
            "symptom_profile": {
                "individual_scores": self.__get_individual_scores(),
            },
        }
