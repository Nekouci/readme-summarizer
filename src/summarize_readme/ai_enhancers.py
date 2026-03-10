"""
AI enhancement providers for intelligent summarization.

Supports free/open-source LLM integrations:
- Hugging Face Inference API (free tier available)
- Ollama (local LLM runtime)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import requests


class AIEnhancer(ABC):
    """Base class for AI enhancement providers."""
    
    @abstractmethod
    def enhance(self, summary: str) -> str:
        """
        Enhance a summary using AI.
        
        Args:
            summary: Raw summary to enhance
        
        Returns:
            Enhanced summary
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass


class HuggingFaceEnhancer(AIEnhancer):
    """
    Enhance summaries using Hugging Face Inference API.
    
    Free tier available at: https://huggingface.co/inference-api
    """
    
    DEFAULT_MODEL = "facebook/bart-large-cnn"
    API_URL = "https://api-inference.huggingface.co/models/{model}"
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
        max_length: int = 150,
        min_length: int = 30,
    ):
        """
        Initialize Hugging Face enhancer.
        
        Args:
            api_token: HuggingFace API token (optional for free tier)
            model: Model name (default: facebook/bart-large-cnn)
            timeout: Request timeout in seconds
            max_length: Maximum length of enhanced summary
            min_length: Minimum length of enhanced summary
        """
        self.api_token = api_token
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        self.max_length = max_length
        self.min_length = min_length
        self.api_url = self.API_URL.format(model=self.model)
    
    def enhance(self, summary: str) -> str:
        """
        Enhance summary using HuggingFace model.
        
        Args:
            summary: Raw summary text
        
        Returns:
            Enhanced summary
        """
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        payload = {
            "inputs": summary,
            "parameters": {
                "max_length": self.max_length,
                "min_length": self.min_length,
                "do_sample": False,
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if "summary_text" in result[0]:
                        return result[0]["summary_text"]
                    elif "generated_text" in result[0]:
                        return result[0]["generated_text"]
                
                # Fallback to original if unexpected format
                return summary
            
            elif response.status_code == 503:
                # Model is loading, return original
                return summary
            
            else:
                # API error, return original
                return summary
        
        except Exception:
            # Network error or timeout, return original
            return summary
    
    def is_available(self) -> bool:
        """Check if HuggingFace API is available."""
        try:
            response = requests.get(
                f"https://huggingface.co/api/models/{self.model}",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


class OllamaEnhancer(AIEnhancer):
    """
    Enhance summaries using Ollama (local LLM runtime).
    
    Ollama provides free local LLM inference. Download from: https://ollama.ai
    """
    
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_HOST = "http://localhost:11434"
    
    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        timeout: int = 30,
        temperature: float = 0.7,
        max_tokens: int = 250,
    ):
        """
        Initialize Ollama enhancer.
        
        Args:
            model: Model name (default: llama3.2)
            host: Ollama server URL
            timeout: Request timeout in seconds
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model or self.DEFAULT_MODEL
        self.host = host or self.DEFAULT_HOST
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def enhance(self, summary: str) -> str:
        """
        Enhance summary using Ollama.
        
        Args:
            summary: Raw summary text
        
        Returns:
            Enhanced, more concise and polished summary
        """
        prompt = f"""You are an expert technical writer. Improve this README summary by making it more concise, clear, and professional. Keep the same key information but enhance readability.

Original summary:
{summary}

Enhanced summary:"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced = result.get("response", "").strip()
                
                # Only return enhanced version if it's valid
                if enhanced and len(enhanced) > 10:
                    return enhanced
            
            # Fallback to original
            return summary
        
        except Exception:
            # Ollama not available or error, return original
            return summary
    
    def is_available(self) -> bool:
        """Check if Ollama is running and available."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


class ChainEnhancer(AIEnhancer):
    """
    Chain multiple AI enhancers together.
    
    Tries enhancers in order, using the first available one.
    """
    
    def __init__(self, enhancers: list[AIEnhancer]):
        """
        Initialize chain enhancer.
        
        Args:
            enhancers: List of AI enhancers to try in order
        """
        self.enhancers = enhancers
    
    def enhance(self, summary: str) -> str:
        """Try each enhancer until one succeeds."""
        for enhancer in self.enhancers:
            if enhancer.is_available():
                try:
                    enhanced = enhancer.enhance(summary)
                    # Only use if different from original
                    if enhanced != summary:
                        return enhanced
                except Exception:
                    continue
        
        # All failed, return original
        return summary
    
    def is_available(self) -> bool:
        """Check if any enhancer is available."""
        return any(e.is_available() for e in self.enhancers)


def create_enhancer(
    provider: str = "none",
    config: Optional[Dict[str, Any]] = None
) -> Optional[AIEnhancer]:
    """
    Factory function to create an AI enhancer.
    
    Args:
        provider: Provider name (huggingface, ollama, chain, none)
        config: Provider-specific configuration
    
    Returns:
        AIEnhancer instance or None
    """
    config = config or {}
    
    if provider == "huggingface":
        return HuggingFaceEnhancer(**config)
    
    elif provider == "ollama":
        return OllamaEnhancer(**config)
    
    elif provider == "chain":
        # Create a chain of available enhancers
        enhancers = []
        
        # Try Ollama first (local, fastest)
        ollama = OllamaEnhancer(**config.get("ollama", {}))
        enhancers.append(ollama)
        
        # Fallback to HuggingFace
        hf = HuggingFaceEnhancer(**config.get("huggingface", {}))
        enhancers.append(hf)
        
        return ChainEnhancer(enhancers)
    
    else:
        return None
