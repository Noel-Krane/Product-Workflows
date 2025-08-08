"""
OpenRouter API client with comprehensive cost tracking and model management.
Provides unified interface for multiple LLM providers via OpenRouter.
"""

import httpx
import json
import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from src.config import get_settings
from src.observability.tracker import CostTracker
import structlog

logger = structlog.get_logger(__name__)

class ModelUsage(BaseModel):
    """Usage statistics for a model call"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    model: str
    timestamp: datetime
    duration_seconds: float

class OpenRouterResponse(BaseModel):
    """Standardized response from OpenRouter"""
    content: str
    usage: ModelUsage
    model: str
    finish_reason: str
    raw_response: Dict[str, Any]

class OpenRouterClient:
    """
    Unified interface for multiple LLM providers via OpenRouter
    with automatic cost tracking and budget enforcement
    """
    
    # Model pricing (per 1M tokens)
    MODEL_PRICING = {
        "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
        "openai/gpt-4o": {"input": 5.0, "output": 15.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "perplexity/llama-3.1-sonar-large-128k-online": {"input": 1.0, "output": 1.0},
        "meta-llama/llama-3.1-8b-instruct:free": {"input": 0.0, "output": 0.0},
    }
    
    # Model selection strategy
    MODELS = {
        "primary": "anthropic/claude-3.5-sonnet",
        "fallback": "openai/gpt-4o-mini", 
        "web_search": "perplexity/llama-3.1-sonar-large-128k-online",
        "cost_effective": "openai/gpt-4o-mini",
        "free": "meta-llama/llama-3.1-8b-instruct:free"
    }
    
    def __init__(self, cost_tracker: Optional[CostTracker] = None):
        self.settings = get_settings()
        self.api_key = self.settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.cost_tracker = cost_tracker or CostTracker()
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
    
    async def call_model(self, 
                        messages: List[Dict[str, str]],
                        model: str = None,
                        max_tokens: int = 4000,
                        temperature: float = 0.7,
                        call_type: str = "general",
                        stream: bool = False) -> OpenRouterResponse:
        """
        Make a call to OpenRouter with automatic cost tracking
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to primary model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            call_type: Type of call for cost tracking
            stream: Whether to stream the response
            
        Returns:
            OpenRouterResponse with content and usage statistics
        """
        if model is None:
            model = self.MODELS["primary"]
        
        # Check budget before making call
        estimated_cost = self._estimate_call_cost(messages, max_tokens, model)
        if not await self.cost_tracker.can_make_call(estimated_cost):
            raise ValueError(f"Budget exceeded. Estimated cost: ${estimated_cost:.4f}")
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.settings.app_url or "http://localhost:8000",
                    "X-Title": "AI Research Platform"
                }
                
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": stream
                }
                
                logger.info("Making OpenRouter API call", 
                           model=model, 
                           call_type=call_type,
                           estimated_cost=estimated_cost)
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                duration = time.time() - start_time
                
                # Extract usage and calculate actual cost
                usage_data = result.get("usage", {})
                input_tokens = usage_data.get("prompt_tokens", 0)
                output_tokens = usage_data.get("completion_tokens", 0)
                total_tokens = usage_data.get("total_tokens", input_tokens + output_tokens)
                
                actual_cost = self._calculate_cost(model, input_tokens, output_tokens)
                
                # Create usage object
                usage = ModelUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost=actual_cost,
                    model=model,
                    timestamp=datetime.utcnow(),
                    duration_seconds=duration
                )
                
                # Track the cost
                await self.cost_tracker.track_api_call(
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=actual_cost,
                    call_type=call_type,
                    duration=duration
                )
                
                # Extract content
                content = ""
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        content = choice["message"].get("content", "")
                    elif "text" in choice:
                        content = choice["text"]
                
                finish_reason = ""
                if "choices" in result and len(result["choices"]) > 0:
                    finish_reason = result["choices"][0].get("finish_reason", "")
                
                logger.info("OpenRouter API call completed",
                           model=model,
                           input_tokens=input_tokens,
                           output_tokens=output_tokens,
                           actual_cost=actual_cost,
                           duration=duration)
                
                return OpenRouterResponse(
                    content=content,
                    usage=usage,
                    model=model,
                    finish_reason=finish_reason,
                    raw_response=result
                )
                
        except httpx.HTTPError as e:
            logger.error("OpenRouter API error", error=str(e), model=model)
            # Try fallback model if primary fails
            if model == self.MODELS["primary"] and model != self.MODELS["fallback"]:
                logger.info("Retrying with fallback model", fallback=self.MODELS["fallback"])
                return await self.call_model(
                    messages=messages,
                    model=self.MODELS["fallback"],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    call_type=call_type,
                    stream=stream
                )
            raise
        except Exception as e:
            logger.error("Unexpected error in OpenRouter call", error=str(e))
            raise
    
    def _estimate_call_cost(self, messages: List[Dict[str, str]], max_tokens: int, model: str) -> float:
        """Estimate the cost of a call before making it"""
        # Rough token estimation (4 chars = 1 token)
        input_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_input_tokens = input_chars // 4
        estimated_output_tokens = max_tokens // 2  # Conservative estimate
        
        return self._calculate_cost(model, estimated_input_tokens, estimated_output_tokens)
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage and model pricing"""
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING["anthropic/claude-3.5-sonnet"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logger.error("Failed to fetch available models", error=str(e))
            return []
    
    async def health_check(self) -> bool:
        """Check if OpenRouter API is accessible"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.call_model(
                messages=test_messages,
                model=self.MODELS["free"],  # Use free model for health check
                max_tokens=10,
                call_type="health_check"
            )
            return bool(response.content)
        except Exception as e:
            logger.error("OpenRouter health check failed", error=str(e))
            return False

# Convenience functions for common use cases
async def quick_call(prompt: str, 
                    model: str = None, 
                    system_message: str = None,
                    call_type: str = "quick_call") -> str:
    """Make a quick call with a simple prompt"""
    client = OpenRouterClient()
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    response = await client.call_model(messages=messages, model=model, call_type=call_type)
    return response.content

async def structured_call(prompt: str,
                         expected_schema: Dict[str, Any],
                         model: str = None,
                         call_type: str = "structured_call") -> Dict[str, Any]:
    """Make a call expecting structured JSON output"""
    system_message = f"""
    You are a helpful assistant that always responds with valid JSON.
    Your response must follow this exact schema:
    {json.dumps(expected_schema, indent=2)}
    
    Return ONLY valid JSON, no additional text or formatting.
    """
    
    content = await quick_call(prompt, model, system_message, call_type)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response", content=content, error=str(e))
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Invalid JSON response: {content}")