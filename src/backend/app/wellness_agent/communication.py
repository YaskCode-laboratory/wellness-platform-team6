"""
Módulo de Comunicación Inter-Agente — Protocolo de Mensajes, Trazabilidad y Prevención de Ciclos.
Define las estructuras InterAgentMessage, InterAgentResponse y DelegationTracer para la plataforma Wellness Lift.
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class InterAgentMessage:
    """
    Estructura estandarizada de mensaje intercambiado entre el Orchestrator Agent y los agentes especializados.
    """

    def __init__(
        self,
        source_agent: str,
        target_agent: str,
        user_id: str,
        intent: str,
        context_payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        hop_count: int = 1,
    ):
        self.task_id = task_id or f"TASK-{uuid.uuid4().hex[:8].upper()}"
        self.trace_id = trace_id or f"TRACE-{uuid.uuid4().hex[:8].upper()}"
        self.source_agent = source_agent
        self.target_agent = target_agent
        self.user_id = user_id
        self.intent = intent
        self.context_payload = context_payload or {}
        self.timestamp = time.time()
        self.hop_count = hop_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "user_id": self.user_id,
            "intent": self.intent,
            "context_payload": self.context_payload,
            "timestamp": self.timestamp,
            "hop_count": self.hop_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterAgentMessage":
        msg = cls(
            source_agent=data.get("source_agent", "UnknownSource"),
            target_agent=data.get("target_agent", "UnknownTarget"),
            user_id=data.get("user_id", "unknown_user"),
            intent=data.get("intent", "GENERAL"),
            context_payload=data.get("context_payload", {}),
            task_id=data.get("task_id"),
            trace_id=data.get("trace_id"),
            hop_count=data.get("hop_count", 1),
        )
        msg.timestamp = data.get("timestamp", time.time())
        return msg


class InterAgentResponse:
    """
    Estructura estandarizada de respuesta retornada por el agente especialista hacia el supervisor.
    """

    def __init__(
        self,
        task_id: str,
        trace_id: str,
        source_agent: str,
        status: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        execution_time_ms: float = 0.0,
    ):
        self.task_id = task_id
        self.trace_id = trace_id
        self.source_agent = source_agent
        self.status = status
        self.content = content
        self.metadata = metadata or {}
        self.execution_time_ms = execution_time_ms

    @property
    def agent_name(self) -> str:
        """Alias para mantener retrocompatibilidad con SpecializedAgentResponse."""
        return self.source_agent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "source_agent": self.source_agent,
            "agent_name": self.source_agent,
            "status": self.status,
            "content": self.content,
            "metadata": self.metadata,
            "execution_time_ms": self.execution_time_ms,
        }


class DelegationTracer:
    """
    Rastreador centralizado de delegaciones inter-agente y prevención de ciclos de llamadas (directos e indirectos).
    """

    def __init__(self, max_hops: int = 5):
        self.max_hops = max_hops
        self._traces: Dict[str, List[Dict[str, Any]]] = {}

    def log_delegation(self, message: InterAgentMessage) -> bool:
        """
        Registra una delegación de mensaje. Retorna False si se detecta un ciclo o excede max_hops.
        """
        if message.hop_count > self.max_hops:
            logger.warning(
                f"DelegationTracer: Se excedió el número máximo de saltos ({self.max_hops}) (actual: {message.hop_count}) en trace '{message.trace_id}'"
            )
            return False

        if message.trace_id not in self._traces:
            self._traces[message.trace_id] = []

        history = self._traces[message.trace_id]

        # Detección de ciclos directos e indirectos (e.g. A -> B -> A o A -> B -> C -> A)
        visited_agents = set()
        for entry in history:
            visited_agents.add(entry["source_agent"])
            visited_agents.add(entry["target_agent"])

        # Si el agente destino ya participó como origen o destino en la cadena activa de la traza, se detecta un ciclo
        if message.target_agent in visited_agents:
            logger.warning(
                f"DelegationTracer: Detectado ciclo de delegación en trace '{message.trace_id}' hacia '{message.target_agent}'. Agentes en la traza: {visited_agents}"
            )
            return False

        history.append({
            "task_id": message.task_id,
            "source_agent": message.source_agent,
            "target_agent": message.target_agent,
            "intent": message.intent,
            "timestamp": message.timestamp,
            "hop_count": message.hop_count,
        })
        return True

    def log_response(self, response: InterAgentResponse) -> None:
        """Registra la respuesta de un agente en la traza correspondiente."""
        if response.trace_id in self._traces:
            for entry in self._traces[response.trace_id]:
                if entry["task_id"] == response.task_id:
                    entry["status"] = response.status
                    entry["execution_time_ms"] = response.execution_time_ms
                    break

    def get_trace_history(self, trace_id: str) -> List[Dict[str, Any]]:
        """Retorna el historial completo de delegaciones para un trace_id."""
        return self._traces.get(trace_id, [])

    def clear_traces(self) -> None:
        """Limpia el almacenamiento de trazas."""
        self._traces.clear()


# Instancia singleton del Rastreador de Delegación
global_tracer = DelegationTracer()
