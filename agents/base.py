"""Base agent interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Base class for all agents. Each agent receives context and returns structured output."""

    name: str = "base"

    @abstractmethod
    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic. Override in subclasses."""
        pass
