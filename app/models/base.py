from abc import ABC, abstractmethod


class BaseAssessment(ABC):
    @property
    @abstractmethod
    def total_score() -> int:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def get_severity_level():  # pragma: no cover
        pass
