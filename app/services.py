"""Business logic layer for capability processing."""

import re
import httpx
from typing import Any
from app.config import settings
from app.exceptions import ModelServiceException, InvalidInputException


class TextSummaryService:
    """Service for text summarization."""
    
    @staticmethod
    def summarize(text: str, max_length: int) -> str:
        """
        Generate a summary of the given text.
        
        If OpenAI API key is configured, uses real model.
        Otherwise, falls back to simple truncation simulation.
        """
        if settings.openai_api_key:
            return TextSummaryService._summarize_with_model(text, max_length)
        return TextSummaryService._summarize_simulated(text, max_length)
    
    @staticmethod
    def _summarize_simulated(text: str, max_length: int) -> str:
        """Simulated summarization by truncation with ellipsis."""
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        if len(text) <= max_length:
            return text
        
        # Try to break at a sentence boundary
        truncated = text[:max_length]
        last_sentence = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_sentence > max_length * 0.7:
            return text[:last_sentence + 1] + " [Summary truncated]"
        elif last_space > max_length * 0.7:
            return text[:last_space] + "... [Summary truncated]"
        else:
            return truncated + "... [Summary truncated]"
    
    @staticmethod
    def _summarize_with_model(text: str, max_length: int) -> str:
        """Summarize using OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that summarizes text concisely. "
                                   f"Provide a summary in no more than {max_length} characters."
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=max_length // 2,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise ModelServiceException(
                message=f"Failed to call model service: {str(e)}",
                details={"provider": "openai", "model": settings.openai_model}
            )


class TextTranslateService:
    """Service for text translation."""
    
    # Simple translation dictionary for simulation
    TRANSLATIONS = {
        ("hello", "zh"): "你好",
        ("hello", "ja"): "こんにちは",
        ("hello", "es"): "Hola",
        ("hello", "fr"): "Bonjour",
        ("world", "zh"): "世界",
        ("world", "ja"): "世界",
        ("thank you", "zh"): "谢谢",
        ("thank you", "ja"): "ありがとう",
        ("good morning", "zh"): "早上好",
        ("good night", "zh"): "晚安",
    }
    
    @classmethod
    def translate(cls, text: str, target_language: str, source_language: str | None = None) -> dict[str, Any]:
        """
        Translate text to target language.
        
        If OpenAI API key is configured, uses real model.
        Otherwise, falls back to simple dictionary simulation.
        """
        if settings.openai_api_key:
            return cls._translate_with_model(text, target_language, source_language)
        return cls._translate_simulated(text, target_language, source_language)
    
    @classmethod
    def _translate_simulated(cls, text: str, target_language: str, source_language: str | None) -> dict[str, Any]:
        """Simulated translation using dictionary lookup."""
        text_lower = text.lower().strip()
        
        # Check dictionary
        translated = cls.TRANSLATIONS.get((text_lower, target_language.lower()))
        
        if translated:
            return {
                "translated_text": translated,
                "source_language": source_language or "auto",
                "target_language": target_language,
                "note": "Translated using simulation mode"
            }
        
        # Fallback: return original with indicator
        return {
            "translated_text": f"[{target_language.upper()}] {text}",
            "source_language": source_language or "auto",
            "target_language": target_language,
            "note": "Translation not available in simulation mode"
        }
    
    @classmethod
    def _translate_with_model(cls, text: str, target_language: str, source_language: str | None) -> dict[str, Any]:
        """Translate using OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            
            source_hint = f"from {source_language}" if source_language else ""
            
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the text {source_hint} "
                                   f"to {target_language}. Return only the translation, no explanation."
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            return {
                "translated_text": response.choices[0].message.content.strip(),
                "source_language": source_language or "auto-detected",
                "target_language": target_language,
                "note": "Translated using OpenAI"
            }
            
        except Exception as e:
            raise ModelServiceException(
                message=f"Failed to call translation service: {str(e)}",
                details={"provider": "openai", "model": settings.openai_model}
            )
