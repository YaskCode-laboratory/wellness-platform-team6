"""
Módulo de Gestión de Proveedores LLM (LLMProviderManager).
Abstrae y encapsula llamadas a OpenRouter, Gemini Cloud, Groq y Motor Local Fallback.
"""

import json
import logging
import os
from typing import Optional, Dict, Any

import httpx

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import groq
except ImportError:
    groq = None

logger = logging.getLogger(__name__)

OPENROUTER_DEFAULT_KEY = "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"


class LLMProviderManager:
    """
    Administrador centralizado para inferencia en modelos de lenguaje externos y locales.
    """

    @staticmethod
    def get_openrouter_key() -> Optional[str]:
        if os.environ.get("DISABLE_EXTERNAL_LLM", "").lower() in ("true", "1", "yes"):
            return None
        return os.environ.get("OPENROUTER_API_KEY", OPENROUTER_DEFAULT_KEY)

    @staticmethod
    def get_gemini_key() -> Optional[str]:
        if os.environ.get("DISABLE_EXTERNAL_LLM", "").lower() in ("true", "1", "yes"):
            return None
        return os.environ.get("GEMINI_API_KEY")

    @staticmethod
    def get_groq_key() -> Optional[str]:
        if os.environ.get("DISABLE_EXTERNAL_LLM", "").lower() in ("true", "1", "yes"):
            return None
        return os.environ.get("GROQ_API_KEY")

    def call_openrouter(self, prompt: str, is_json: bool = False) -> Optional[str]:
        """Realiza una petición a la API de OpenRouter."""
        key = self.get_openrouter_key()
        if not key:
            return None

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Wellness App"
        }
        models = ["inclusionai/ling-3.0-flash:free", "openrouter/auto", "google/gemma-4-31b-it:free"]

        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2 if is_json else 0.7
                }
                with httpx.Client(timeout=3.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0]["message"]["content"]
                    logger.warning(f"OpenRouter model {model} status {resp.status_code}")
            except Exception as e:
                logger.warning(f"Error llamando OpenRouter ({model}): {e}")
                continue
        return None

    def call_gemini(self, prompt: str) -> Optional[str]:
        """Realiza una petición a la API de Google Gemini."""
        gemini_key = self.get_gemini_key()
        if gemini_key and genai:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Error llamando Gemini: {e}")
        return None

    def call_groq(self, prompt: str, is_json: bool = False) -> Optional[str]:
        """Realiza una petición a la API de Groq."""
        groq_key = self.get_groq_key()
        if groq_key and groq:
            try:
                client = groq.Groq(api_key=groq_key)
                models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
                for model_name in models_to_try:
                    try:
                        kwargs: Dict[str, Any] = {
                            "messages": [{"role": "user", "content": prompt}],
                            "model": model_name,
                            "temperature": 0.2 if is_json else 0.7,
                        }
                        if is_json:
                            kwargs["response_format"] = {"type": "json_object"}
                        response = client.chat.completions.create(**kwargs)
                        if response.choices:
                            return response.choices[0].message.content.strip()
                    except Exception as ex:
                        logger.warning(f"Error Groq modelo {model_name}: {ex}")
                        continue
            except Exception as e:
                logger.warning(f"Error inicializando Groq: {e}")
        return None

    def generate_completion(self, prompt: str, is_json: bool = False) -> Optional[str]:
        """
        Intenta generar una respuesta pasando ordenadamente por los proveedores externos disponibles.
        Retorna None si ningún proveedor responde.
        """
        # 1. OpenRouter
        res = self.call_openrouter(prompt, is_json=is_json)
        if res:
            return res

        # 2. Gemini
        res = self.call_gemini(prompt)
        if res:
            return res

        # 3. Groq
        res = self.call_groq(prompt, is_json=is_json)
        if res:
            return res

        return None
