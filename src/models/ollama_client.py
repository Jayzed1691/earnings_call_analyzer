"""
Ollama client wrapper for LLM-based analysis tasks
"""
import json
from typing import Dict, Any, List, Optional
import ollama
from config.settings import settings


class OllamaClient:
    """Wrapper for Ollama API interactions"""
    
    def __init__(self, host: str = None, timeout: int = None):
        """
        Initialize Ollama client
        
        Args:
            host: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.host = host or settings.OLLAMA_HOST
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        self.client = ollama.Client(host=self.host)
    
    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate completion from Ollama model
        
        Args:
            model: Model name (e.g., 'llama3.1:8b')
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Whether to request JSON output
            
        Returns:
            Generated text or JSON string
        """
        temperature = temperature or settings.LLM_TEMPERATURE
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
        
        format_param = "json" if json_mode else None
        
        try:
            response = self.client.chat(
                model=model,
                messages=messages,
                options=options,
                format=format_param
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Ollama model
        
        Args:
            text: Text segment to analyze
            
        Returns:
            Dict with sentiment label and confidence
        """
        system_prompt = """You are a financial sentiment analyzer. 
        Analyze the sentiment of earnings call transcript segments.
        Classify as: Positive, Negative, or Neutral.
        Provide a confidence score (0.0-1.0)."""
        
        user_prompt = f"""Analyze the sentiment of this earnings call segment:

"{text}"

Respond in JSON format:
{{
    "sentiment": "Positive|Negative|Neutral",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""
        
        response = self.generate(
            model=settings.SENTIMENT_MODEL,
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_mode=True
        )
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "reasoning": "Failed to parse LLM response"
            }
    
    def assess_contextualization(self, number: str, context: str) -> Dict[str, Any]:
        """
        Assess how well a number is contextualized
        
        Args:
            number: The numerical value
            context: Surrounding context (sentence)
            
        Returns:
            Dict with contextualization score and components
        """
        system_prompt = """You are a financial communication analyst.
        Assess whether numbers in earnings calls are well-contextualized.
        
        A well-contextualized number should have:
        1. Comparison (vs prior period, target, benchmark)
        2. Explanation (driver or reason)
        3. Implication (what it means for the business)"""
        
        user_prompt = f"""Assess the contextualization of this number:

Number: {number}
Context: "{context}"

Rate each component (0-1):
- has_comparison: Does it compare to something?
- has_explanation: Is there a reason/driver?
- has_implication: Is the business impact stated?

Respond in JSON:
{{
    "has_comparison": 0.0-1.0,
    "has_explanation": 0.0-1.0,
    "has_implication": 0.0-1.0,
    "overall_score": 0.0-3.0,
    "category": "Well-Contextualized|Moderately Contextualized|Minimally Contextualized|Undercontextualized"
}}"""
        
        response = self.generate(
            model=settings.CONTEXTUALIZATION_MODEL,
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_mode=True
        )
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            return {
                "has_comparison": 0.5,
                "has_explanation": 0.5,
                "has_implication": 0.5,
                "overall_score": 1.5,
                "category": "Moderately Contextualized"
            }
    
    def check_model_availability(self, model: str) -> bool:
        """
        Check if a model is available locally
        
        Args:
            model: Model name
            
        Returns:
            True if model is available
        """
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models['models']]
            return model in model_names
        except Exception:
            return False
    
    def pull_model(self, model: str) -> None:
        """
        Pull a model from Ollama registry
        
        Args:
            model: Model name to pull
        """
        try:
            self.client.pull(model)
            print(f"Successfully pulled model: {model}")
        except Exception as e:
            raise RuntimeError(f"Failed to pull model {model}: {str(e)}")


# Global client instance
ollama_client = OllamaClient()
