"""
Ollama client wrapper for LLM-based analysis tasks
Enhanced with retry logic and comprehensive error handling
"""
import json
import logging
from typing import Dict, Any, List, Optional
import ollama
from config.settings import settings
from src.utils.retry import exponential_backoff_retry, with_fallback

logger = logging.getLogger(__name__)


class OllamaClient:
    """Wrapper for Ollama API interactions"""
    
    def __init__(self, host: str = None, timeout: int = None, max_retries: int = 3):
        """
        Initialize Ollama client

        Args:
            host: Ollama server URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.host = host or settings.OLLAMA_HOST
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        self.max_retries = max_retries
        self.client = ollama.Client(host=self.host)
        logger.info(f"Initialized Ollama client: {self.host}, max_retries={max_retries}")
    
    @exponential_backoff_retry(
        max_attempts=3,
        initial_delay=2.0,
        exceptions=(ConnectionError, TimeoutError, RuntimeError),
        log_attempts=True
    )
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
        Generate completion from Ollama model with retry logic

        Args:
            model: Model name (e.g., 'llama3.1:8b')
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Whether to request JSON output

        Returns:
            Generated text or JSON string

        Raises:
            RuntimeError: If generation fails after all retries
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
            logger.debug(f"Calling Ollama: model={model}, json_mode={json_mode}")
            response = self.client.chat(
                model=model,
                messages=messages,
                options=options,
                format=format_param
            )

            content = response['message']['content']
            logger.debug(f"Ollama response received: {len(content)} chars")
            return content

        except ConnectionError as e:
            logger.error(f"Connection error to Ollama: {e}")
            raise RuntimeError(f"Cannot connect to Ollama at {self.host}: {str(e)}")
        except TimeoutError as e:
            logger.error(f"Ollama request timed out: {e}")
            raise RuntimeError(f"Ollama request timed out after {self.timeout}s: {str(e)}")
        except KeyError as e:
            logger.error(f"Invalid Ollama response format: {e}")
            raise RuntimeError(f"Invalid response from Ollama: missing {str(e)}")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using Ollama model with error handling

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

        try:
            response = self.generate(
                model=settings.SENTIMENT_MODEL,
                prompt=user_prompt,
                system_prompt=system_prompt,
                json_mode=True
            )

            result = json.loads(response)

            # Validate response structure
            self._validate_sentiment_response(result)
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return self._neutral_sentiment_fallback("JSON parse error")
        except RuntimeError as e:
            logger.warning(f"LLM call failed: {e}")
            return self._neutral_sentiment_fallback("LLM unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in sentiment analysis: {e}", exc_info=True)
            return self._neutral_sentiment_fallback("Unexpected error")

    def _validate_sentiment_response(self, result: Dict[str, Any]) -> None:
        """Validate sentiment analysis response"""
        required_keys = ['sentiment', 'confidence']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key: {key}")

        if result['sentiment'] not in ['Positive', 'Negative', 'Neutral']:
            logger.warning(f"Invalid sentiment: {result['sentiment']}, defaulting to Neutral")
            result['sentiment'] = 'Neutral'

        if not (0.0 <= result['confidence'] <= 1.0):
            logger.warning(f"Invalid confidence: {result['confidence']}, clamping to [0,1]")
            result['confidence'] = max(0.0, min(1.0, result['confidence']))

    def _neutral_sentiment_fallback(self, reason: str) -> Dict[str, Any]:
        """Return neutral sentiment as fallback"""
        logger.info(f"Using neutral sentiment fallback: {reason}")
        return {
            "sentiment": "Neutral",
            "confidence": 0.5,
            "reasoning": f"Fallback due to: {reason}"
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
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse contextualization response: {e}")
            return {
                "has_comparison": 0.5,
                "has_explanation": 0.5,
                "has_implication": 0.5,
                "overall_score": 1.5,
                "category": "Moderately Contextualized"
            }
        except Exception as e:
            logger.error(f"Contextualization analysis failed: {e}")
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
            logger.info(f"Pulling model: {model}")
            self.client.pull(model)
            logger.info(f"Successfully pulled model: {model}")
        except Exception as e:
            logger.error(f"Failed to pull model {model}: {e}")
            raise RuntimeError(f"Failed to pull model {model}: {str(e)}")


# Global client instance
ollama_client = OllamaClient()
