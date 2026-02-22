"""Base Agent class for PlanIT multi-agent system.

All specialized agents inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client import get_client, BaseLLMClient


class BaseAgent(ABC):
    """Abstract base class for all PlanIT agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm: BaseLLMClient = get_client()
        self._conversation_history: List[Dict[str, str]] = []

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a message and return a response.
        
        Args:
            message: The user message to process.
            context: Optional context from other agents or the orchestrator.
            
        Returns:
            The agent's response string.
        """
        # Add context to the message if provided
        if context:
            enhanced_message = f"{message}\n\nContext: {context}"
        else:
            enhanced_message = message

        # Add to conversation history
        self._conversation_history.append({"role": "user", "content": enhanced_message})

        # Get response from LLM
        response = await self.llm.chat(
            messages=self._conversation_history,
            system_prompt=self.system_prompt,
        )

        # Add response to history
        self._conversation_history.append({"role": "assistant", "content": response})

        return response

    def reset_conversation(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []

    def get_status(self) -> Dict[str, Any]:
        """Return the agent's current status."""
        return {
            "name": self.name,
            "description": self.description,
            "conversation_length": len(self._conversation_history),
        }
