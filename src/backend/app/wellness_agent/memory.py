"""
Módulo de Gestión de Memoria Conversacional (ConversationMemoryManager).
Almacena y gestiona el historial de interacciones por usuario para mantener el contexto en diálogos multi-turno.
"""

from typing import Dict, List, Any, Optional


class ConversationMemoryManager:
    """
    Administrador de memoria en tiempo de ejecución para mantener el historial de conversaciones por usuario.
    """

    def __init__(self, max_history_turns: int = 10):
        self.max_history_turns = max_history_turns
        self._memory_store: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Agrega un mensaje (user o assistant) al historial del usuario."""
        if user_id not in self._memory_store:
            self._memory_store[user_id] = []

        self._memory_store[user_id].append({
            "role": role,
            "content": content
        })

        # Mantener solo los últimos max_history_turns * 2 mensajes (pares user/assistant)
        if len(self._memory_store[user_id]) > (self.max_history_turns * 2):
            self._memory_store[user_id] = self._memory_store[user_id][-(self.max_history_turns * 2):]

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """Retorna el historial completo de conversación del usuario."""
        return self._memory_store.get(user_id, [])

    def get_formatted_history(self, user_id: str) -> str:
        """Retorna el historial en formato de texto continuo para inyección en el prompt."""
        history = self.get_history(user_id)
        if not history:
            return ""

        formatted_lines = []
        for msg in history:
            role_label = "Usuario" if msg["role"] == "user" else "Asistente"
            formatted_lines.append(f"{role_label}: {msg['content']}")

        return "\n".join(formatted_lines)

    def clear_memory(self, user_id: str) -> None:
        """Limpia la memoria conversacional de un usuario específico."""
        if user_id in self._memory_store:
            del self._memory_store[user_id]
