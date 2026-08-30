"""
Módulo de Gestión de Memoria Conversacional (ConversationMemoryManager).
Implementa memoria de doble nivel:
1. Memoria a Corto Plazo (Short-Term Buffer): Mantiene turnos recientes para inyección directa en el prompt del LLM.
2. Memoria a Largo Plazo (Long-Term Persistence): Persistencia del historial completo de conversación y hechos clave del usuario.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from app import database

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


class ConversationMemoryManager:
    """
    Administrador de memoria conversacional de doble nivel para el Wellness Coach Agent 2.0.
    """

    def __init__(self, max_history_turns: int = 10, storage_dir: Optional[Path] = None):
        self.max_history_turns = max_history_turns
        self.storage_dir = storage_dir or (ROOT_DIR / "data" / "memory")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._memory_store: Dict[str, List[Dict[str, Any]]] = {}
        self._extracted_facts: Dict[str, List[str]] = {}

    def add_message(self, user_id: str, role: str, content: str, timestamp: Optional[str] = None) -> None:
        """Agrega un mensaje (user o assistant) al historial del usuario y analiza hechos clave."""
        if user_id not in self._memory_store:
            self._memory_store[user_id] = []

        message_obj = {
            "role": role,
            "content": content,
            "timestamp": timestamp or ""
        }

        self._memory_store[user_id].append(message_obj)

        if role == "user":
            self.extract_and_save_facts(user_id, content)

        # Truncamiento de ventana para el buffer de memoria a corto plazo
        if len(self._memory_store[user_id]) > (self.max_history_turns * 2):
            self._memory_store[user_id] = self._memory_store[user_id][-(self.max_history_turns * 2):]

        self.save_to_persistence(user_id)

    def extract_and_save_facts(self, user_id: str, message: str) -> List[str]:
        """Identifica automáticamente lesiones, dolores o logros declarados por el usuario."""
        if user_id not in self._extracted_facts:
            self._extracted_facts[user_id] = []

        msg_lower = message.lower()
        new_facts = []

        # Detección de lesiones y dolores
        if any(k in msg_lower for k in ["hernia", "lumbar", "espalda"]):
            new_facts.append("Condición reportada en chat: Dolor o molestia lumbar / hernia.")
        if any(k in msg_lower for k in ["rodilla", "menisco", "ligamento"]):
            new_facts.append("Condición reportada en chat: Molestia en articulación de rodilla.")
        if any(k in msg_lower for k in ["hombro", "manguito", "rotador"]):
            new_facts.append("Condición reportada en chat: Molestia en hombro / manguito rotador.")

        # Detección de récords o marcas
        record_match = re.search(r"(\d+)\s*kg", msg_lower)
        if record_match:
            weight_val = record_match.group(1)
            new_facts.append(f"Marca reportada en chat: {weight_val} kg.")

        for fact in new_facts:
            if fact not in self._extracted_facts[user_id]:
                self._extracted_facts[user_id].append(fact)

        return self._extracted_facts[user_id]

    def get_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna el historial de conversación del usuario. Si no está en memoria, intenta cargar de disco."""
        if user_id not in self._memory_store:
            self.load_from_persistence(user_id)

        history = self._memory_store.get(user_id, [])
        if limit and limit > 0:
            return history[-limit:]
        return history

    def get_extracted_facts(self, user_id: str) -> List[str]:
        """Retorna la lista de hechos clave extraídos de las conversaciones del usuario."""
        return self._extracted_facts.get(user_id, [])

    def get_formatted_history(self, user_id: str, limit: Optional[int] = None) -> str:
        """Retorna el historial reciente en formato de texto continuo para inyección en prompts."""
        history = self.get_history(user_id, limit=limit)
        if not history:
            return "Sin historial de conversación previa."

        formatted_lines = []
        for msg in history:
            role_label = "Usuario" if msg["role"] == "user" else "Asistente"
            formatted_lines.append(f"{role_label}: {msg['content']}")

        return "\n".join(formatted_lines)

    def save_to_persistence(self, user_id: str) -> None:
        """Persiste el historial de conversación y los hechos extraídos en archivo JSON."""
        file_path = self.storage_dir / f"{user_id}_memory.json"
        data = {
            "user_id": user_id,
            "extracted_facts": self._extracted_facts.get(user_id, []),
            "history": self._memory_store.get(user_id, [])
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error guardando memoria persistente para {user_id}: {e}")

    def load_from_persistence(self, user_id: str) -> bool:
        """Carga el historial y los hechos extraídos desde el almacenamiento persistente."""
        file_path = self.storage_dir / f"{user_id}_memory.json"
        if not file_path.exists():
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._memory_store[user_id] = data.get("history", [])
            self._extracted_facts[user_id] = data.get("extracted_facts", [])
            return True
        except Exception as e:
            logger.warning(f"Error cargando memoria persistente para {user_id}: {e}")
            return False

    def clear_memory(self, user_id: str) -> None:
        """Limpia el buffer de memoria a corto plazo y la persistencia del usuario."""
        if user_id in self._memory_store:
            del self._memory_store[user_id]
        if user_id in self._extracted_facts:
            del self._extracted_facts[user_id]

        file_path = self.storage_dir / f"{user_id}_memory.json"
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.warning(f"Error eliminando archivo de memoria para {user_id}: {e}")
