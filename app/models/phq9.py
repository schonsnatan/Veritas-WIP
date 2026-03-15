from enum import Enum

from pydantic import BaseModel, Field

from app.models.base import BaseAssessment


class SeverityLevel(str, Enum):
    NONE = "Ausência de depressão."
    LOW = "Depressão leve."
    MODERATE = "Depressão moderada."
    HIGH = "Depressão moderadamente grave."
    SEVERE = "Depressão grave."


class PHQ9Assessment(BaseModel, BaseAssessment):
    q1_interest: int = Field(..., ge=0, le=3, description="Pouco interesse ou prazer em fazer coisas.")
    q2_desanimado: int = Field(
        ...,
        ge=0,
        le=3,
        description="Sentir-se desanimado(a), deprimido(a) ou sem esperança.",
    )
    q3_problemas_sono: int = Field(..., ge=0, le=3, description="Dificuldade para dormir ou dormir em excesso.")
    q4_sentir_cansado: int = Field(..., ge=0, le=3, description="Sentir-se cansado(a) ou ter pouca energia")
    q5_comida: int = Field(..., ge=0, le=3, description="Falta de apetite ou comer em excesso")
    q6_fracasso: int = Field(
        ...,
        ge=0,
        le=3,
        description="Sentir-se mal consigo mesmo(a), sentir-se um(a) fracassado(a) ou "
        "achar que decepciona as pessoas próximas",
    )
    q7_concentracao: int = Field(
        ...,
        ge=0,
        le=3,
        description="Dificuldade para se concentrar em coisas, como leitura ou assistir televisão",
    )
    q8_inquietude: int = Field(
        ...,
        ge=0,
        le=3,
        description="Mover-se ou falar devagar, ou o contrário, ficar inquieto(a) e incapaz de ficar parado(a)",
    )
    q9_pen_suicida: int = Field(
        ...,
        ge=0,
        le=3,
        description="Pensamentos de que seria melhor estar morto(a) ou de se machucar de alguma forma",
    )

    @property
    def total_score(self) -> int:
        return sum(
            [
                self.q1_interest,
                self.q2_desanimado,
                self.q3_problemas_sono,
                self.q4_sentir_cansado,
                self.q5_comida,
                self.q6_fracasso,
                self.q7_concentracao,
                self.q8_inquietude,
                self.q9_pen_suicida,
            ]
        )

    @property
    def get_severity_level(self) -> SeverityLevel:
        severity_score = self.total_score
        if severity_score <= 4:
            return SeverityLevel.NONE
        elif 5 <= severity_score <= 9:
            return SeverityLevel.LOW
        elif 10 <= severity_score <= 14:
            return SeverityLevel.MODERATE
        elif 15 <= severity_score <= 19:
            return SeverityLevel.HIGH
        elif 20 <= severity_score <= 27:
            return SeverityLevel.SEVERE

    @property
    def has_crisis_indicator(self) -> bool:
        return self.q9_pen_suicida > 0

    def __get_severity_range(self) -> str:
        """Get the score range for current severity level"""
        ranges = {
            "NONE": "0-4",
            "LOW": "5-9",
            "MODERATE": "10-14",
            "HIGH": "15-19",
            "SEVERE": "20-27",
        }
        return ranges[self.get_severity_level.name]

    def __get_individual_scores(self) -> dict:
        """Get all question scores with labels"""
        return {
            "interest_pleasure": {
                "score": self.q1_interest,
                "label": "Perda de interesse ou prazer",
                "clinical_term": "Anedonia",
            },
            "depressed_mood": {
                "score": self.q2_desanimado,
                "label": "Sentir-se desanimado ou sem esperança",
                "clinical_term": "Humor deprimido",
            },
            "sleep": {
                "score": self.q3_problemas_sono,
                "label": "Problemas de sono",
                "clinical_term": "Distúrbio do sono",
            },
            "fatigue": {
                "score": self.q4_sentir_cansado,
                "label": "Fadiga ou baixa energia",
                "clinical_term": "Fadiga",
            },
            "appetite": {
                "score": self.q5_comida,
                "label": "Mudanças no apetite",
                "clinical_term": "Alteração do apetite",
            },
            "self_worth": {
                "score": self.q6_fracasso,
                "label": "Sentir-se fracassado ou culpado",
                "clinical_term": "Baixa autoestima/culpa",
            },
            "concentration": {
                "score": self.q7_concentracao,
                "label": "Dificuldade de concentração",
                "clinical_term": "Déficit de concentração",
            },
            "psychomotor": {
                "score": self.q8_inquietude,
                "label": "Agitação ou lentidão",
                "clinical_term": "Alteração psicomotora",
            },
            "suicidal_ideation": {
                "score": self.q9_pen_suicida,
                "label": "Pensamentos de morte ou automutilação",
                "clinical_term": "Ideação suicida",
            },
        }

    def to_llm_context(self) -> dict:
        return {
            "assessment_type": "PHQ-9",
            "assessment_name": "Patient Health Questionnaire-9 (Depression)",
            "language": "pt-br",
            "scores": {
                "total": self.total_score,
                "max_possible": 27,
                "percentage": round((self.total_score / 27) * 100, 1),
            },
            "severity": {
                "level": self.get_severity_level,
                "clinical_range": self.__get_severity_range(),
            },
            "crisis_indicators": {
                "has_crisis": self.has_crisis_indicator,
                "suicidal_ideation_score": self.q9_pen_suicida,
                "requires_immediate_attention": self.q9_pen_suicida >= 2,
            },
            "symptom_profile": {
                "individual_scores": self.__get_individual_scores(),
            },
        }
