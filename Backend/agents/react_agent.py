"""ReAct Agent - Reasoning and Acting Agent.

Implements the ReAct pattern where the LLM:
1. THINKS about what to do
2. DECIDES which tool to use
3. ACTS by calling the tool
4. OBSERVES the result
5. Repeats until task is complete
"""

from typing import Dict, Any, List, Optional
import json
import re

from llm_client import get_client
from agents.tools import TOOL_DEFINITIONS, execute_tool, get_tools_prompt


class ReActAgent:
    """ReAct agent that autonomously reasons and uses tools."""
    
    MAX_ITERATIONS = 8  # Prevent infinite loops
    
    def __init__(self):
        self.llm = get_client()
        self.conversation_history: List[Dict[str, str]] = []
    
    @property
    def system_prompt(self) -> str:
        tools_info = get_tools_prompt()
        
        return f"""You are an intelligent travel planning agent for PlanIT. You can use tools to help users plan their trips.

## Available Tools
{tools_info}

## How to Use Tools
When you need information, respond with a tool call in this EXACT format:
```
TOOL: tool_name
ARGS: {{"param1": "value1", "param2": "value2"}}
```

## Rules
1. THINK first about what information you need
2. Call ONE tool at a time
3. Wait for the result before calling another tool
4. After getting enough information, provide a FINAL ANSWER
5. Be specific and helpful in your responses

## CRITICAL INSTRUCTIONS
- **Unknown Destinations**: If the user asks about a place NOT in your internal knowledge (i.e., not Paris/Tokyo), you MUST use `search_web` to find real attractions, prices, and tips. DO NOT HALLUCINATE or give generic advice.
- **Indian Travel**: If the user asks about India or mentions INR/₹, ALWAYS use `calculate_budget` with `currency="INR"` to get accurate local pricing.
- **Web First**: For prices, opening hours, or specific details about non-major cities, prefer `search_web` over other tools.

## Response Format
- If you need to use a tool, start with your reasoning, then the tool call
- If you have enough information, provide your final answer directly
- Always be helpful and provide detailed travel recommendations

## Example
User: "What's the weather like in Paris?"

Your response:
I'll check the weather in Paris for you.

TOOL: get_weather
ARGS: {{"location": "Paris"}}

(After receiving result, you would then provide the answer)
"""

    async def process(self, user_message: str) -> Dict[str, Any]:
        """Process a user message through the ReAct loop.
        
        Returns:
            Dictionary with 'response', 'tool_calls', and 'iterations'
        """
        self.conversation_history.append({"role": "user", "content": user_message})
        
        tool_calls = []
        iterations = 0
        accumulated_context = f"User request: {user_message}\n\n"
        
        while iterations < self.MAX_ITERATIONS:
            iterations += 1
            
            # Build the current prompt with accumulated context
            current_prompt = accumulated_context
            if tool_calls:
                current_prompt += "Based on the information gathered, continue helping the user.\n"
                current_prompt += "If you have enough information, provide your FINAL ANSWER.\n"
                current_prompt += "If you need more information, call another tool.\n"
            
            # Get LLM response
            messages = [{"role": "user", "content": current_prompt}]
            response = await self.llm.chat(messages, system_prompt=self.system_prompt)
            
            # Check if response contains a tool call
            tool_call = self._parse_tool_call(response)
            
            if tool_call:
                tool_name = tool_call["name"]
                tool_args = tool_call["arguments"]
                
                # Execute the tool
                print(f"🔧 Calling tool: {tool_name} with args: {tool_args}")
                result = execute_tool(tool_name, tool_args)
                
                tool_calls.append({
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": result
                })
                
                # Add result to context for next iteration
                accumulated_context += f"\n--- Tool Call ---\n"
                accumulated_context += f"Tool: {tool_name}\n"
                accumulated_context += f"Arguments: {json.dumps(tool_args)}\n"
                accumulated_context += f"Result: {json.dumps(result, indent=2)}\n"
                accumulated_context += f"--- End Tool Call ---\n\n"
                
            else:
                # No tool call - this is the final response
                # Clean up the response (remove any partial tool syntax)
                final_response = self._clean_response(response)
                
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": final_response
                })
                
                return {
                    "response": final_response,
                    "tool_calls": tool_calls,
                    "iterations": iterations
                }
        
        # Max iterations reached - generate final response
        messages = [{"role": "user", "content": accumulated_context + "\nPlease provide your final answer now."}]
        final_response = await self.llm.chat(messages, system_prompt=self.system_prompt)
        final_response = self._clean_response(final_response)
        
        return {
            "response": final_response,
            "tool_calls": tool_calls,
            "iterations": iterations,
            "max_iterations_reached": True
        }
    
    def _parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse a tool call from the LLM response.
        
        Looks for pattern:
        TOOL: tool_name
        ARGS: {"param": "value"}
        """
        # Pattern to match TOOL: name and ARGS: {json}
        tool_pattern = r'TOOL:\s*(\w+)'
        args_pattern = r'ARGS:\s*(\{[^}]+\})'
        
        tool_match = re.search(tool_pattern, response, re.IGNORECASE)
        args_match = re.search(args_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if tool_match:
            tool_name = tool_match.group(1).strip()
            
            # Try to parse arguments
            arguments = {}
            if args_match:
                try:
                    args_str = args_match.group(1)
                    # Fix common JSON issues
                    args_str = args_str.replace("'", '"')
                    arguments = json.loads(args_str)
                except json.JSONDecodeError:
                    # Try to extract key-value pairs manually
                    pass
            
            return {"name": tool_name, "arguments": arguments}
        
        return None
    
    def _clean_response(self, response: str) -> str:
        """Remove tool call syntax from final response."""
        # Remove TOOL: and ARGS: lines
        lines = response.split('\n')
        cleaned_lines = []
        skip_next = False
        
        for line in lines:
            if re.match(r'^\s*TOOL:\s*', line, re.IGNORECASE):
                skip_next = True
                continue
            if re.match(r'^\s*ARGS:\s*', line, re.IGNORECASE):
                continue
            if skip_next and line.strip().startswith('{'):
                skip_next = False
                continue
            skip_next = False
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []


# Factory function
def create_react_agent() -> ReActAgent:
    """Create and return a ReAct agent."""
    return ReActAgent()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ReActAgent()
        
        # Test query
        result = await agent.process(
            "Plan a 3-day trip to Paris. What's the weather like and how much will it cost for 2 people?"
        )
        
        print("=" * 50)
        print("TOOL CALLS:")
        for tc in result["tool_calls"]:
            print(f"  - {tc['tool']}: {tc['arguments']}")
        print(f"\nITERATIONS: {result['iterations']}")
        print("\nFINAL RESPONSE:")
        print(result["response"])
    
    asyncio.run(test())
