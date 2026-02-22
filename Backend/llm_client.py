"""Unified LLM client for PlanIT.

Supports OpenAI, Google Gemini, and a mock mode for development.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json

from config import settings


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send messages to the LLM and get a response."""
        pass

    @abstractmethod
    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Chat with function calling support."""
        pass


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for development without API keys."""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Return a mock response based on the last user message."""
        last_message = messages[-1]["content"] if messages else ""
        
        # Simple mock responses for development
        if "plan" in last_message.lower() or "trip" in last_message.lower():
            return (
                "I'd be happy to help plan your trip! Based on your request, "
                "here's a suggested itinerary:\n\n"
                "**Day 1**: Arrive and explore the local area\n"
                "**Day 2**: Visit main attractions\n"
                "**Day 3**: Day trip to nearby destinations\n\n"
                "Would you like me to add more details or adjust this plan?"
            )
        elif "budget" in last_message.lower() or "cost" in last_message.lower():
            return (
                "Based on typical costs for this type of trip:\n\n"
                "- Accommodation: $100-150/night\n"
                "- Food: $50-75/day\n"
                "- Activities: $30-50/day\n"
                "- Transportation: $20-40/day\n\n"
                "Total estimated daily budget: $200-315"
            )
        else:
            return (
                f"I understand you're asking about: {last_message[:100]}...\n\n"
                "I'm the PlanIT assistant. I can help you plan trips, "
                "estimate budgets, and find great destinations. "
                "What would you like to explore?"
            )

    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return a mock function call response."""
        return {
            "type": "message",
            "content": await self.chat(messages, system_prompt),
        }


class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""

    def __init__(self):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send messages to OpenAI and get a response."""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
        )
        
        return response.choices[0].message.content

    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Chat with function calling support."""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        # Convert to OpenAI tools format
        tools = [{"type": "function", "function": f} for f in functions]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            tools=tools if tools else None,
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "type": "function_call",
                "name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments),
            }
        
        return {
            "type": "message",
            "content": message.content,
        }


class GeminiClient(BaseLLMClient):
    """Google Gemini API client."""

    def __init__(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send messages to Gemini and get a response."""
        # Build the full prompt from messages
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}\n")
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}")
        
        full_prompt = "\n".join(prompt_parts)
        
        # Use synchronous generate_content (works better with Flask)
        response = self.model.generate_content(
            full_prompt,
            generation_config={"temperature": temperature},
        )
        
        return response.text

    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Chat with function calling (basic support)."""
        # Gemini function calling support - simplified
        response = await self.chat(messages, system_prompt)
        return {
            "type": "message",
            "content": response,
        }


class GroqClient(BaseLLMClient):
    """Groq API client for fast LLM inference."""

    def __init__(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=settings.groq_api_key)
            self.model = settings.groq_model
        except ImportError:
            raise ImportError(
                "groq package not installed. "
                "Run: pip install groq"
            )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Send messages to Groq and get a response."""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        # Groq uses synchronous API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
        )
        
        return response.choices[0].message.content

    async def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Chat with function calling support."""
        response = await self.chat(messages, system_prompt)
        return {
            "type": "message",
            "content": response,
        }


def get_llm_client() -> BaseLLMClient:
    """Factory function to get the appropriate LLM client."""
    provider = settings.llm_provider.lower()
    
    if provider == "openai":
        if not settings.openai_api_key:
            print("Warning: OPENAI_API_KEY not set, falling back to mock mode")
            return MockLLMClient()
        return OpenAIClient()
    
    elif provider == "gemini":
        if not settings.google_api_key:
            print("Warning: GOOGLE_API_KEY not set, falling back to mock mode")
            return MockLLMClient()
        return GeminiClient()
    
    elif provider == "groq":
        if not settings.groq_api_key:
            print("Warning: GROQ_API_KEY not set, falling back to mock mode")
            return MockLLMClient()
        return GroqClient()
    
    else:
        return MockLLMClient()


# Global client instance
_llm_client: Optional[BaseLLMClient] = None


def get_client() -> BaseLLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client
