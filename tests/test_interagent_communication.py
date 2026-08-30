"""
Suite de Pruebas Automatizadas para la Comunicación e Interoperabilidad Inter-Agente (Issue #22 - S3-04).
Verifica serialización de mensajes, trazabilidad, prevención de ciclos y documentación de evolución MCP/A2A.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.wellness_agent.communication import InterAgentMessage, InterAgentResponse, DelegationTracer
from app.orchestrator import OrchestratorAgent, AgentIntent


def test_message_serialization_deserialization():
    """Verifica la correcta conversión a diccionario y restauración de InterAgentMessage."""
    msg = InterAgentMessage(
        source_agent="OrchestratorAgent",
        target_agent="WellnessCoachAgent2.0",
        user_id="user_test_comm",
        intent="WORKOUT_BIOMECHANICS",
        context_payload={"query": "Sentadillas seguras"}
    )
    d = msg.to_dict()

    assert d["source_agent"] == "OrchestratorAgent"
    assert d["target_agent"] == "WellnessCoachAgent2.0"
    assert d["intent"] == "WORKOUT_BIOMECHANICS"
    assert d["hop_count"] == 1

    restored = InterAgentMessage.from_dict(d)
    assert restored.task_id == msg.task_id
    assert restored.trace_id == msg.trace_id
    assert restored.user_id == "user_test_comm"


def test_delegation_tracer_and_cycle_prevention():
    """Verifica el rastreo de trazas y la prevención de ciclos de delegación."""
    tracer = DelegationTracer(max_hops=3)

    msg1 = InterAgentMessage(
        source_agent="OrchestratorAgent",
        target_agent="WellnessCoachAgent2.0",
        user_id="u1",
        intent="WORKOUT_BIOMECHANICS",
        hop_count=1
    )
    assert tracer.log_delegation(msg1) is True

    # Mensaje con hop_count excedido
    msg_exceeded = InterAgentMessage(
        source_agent="AgentA",
        target_agent="AgentB",
        user_id="u1",
        intent="TEST",
        hop_count=4
    )
    assert tracer.log_delegation(msg_exceeded) is False, "Debe rechazar cuando hop_count > max_hops"

    # Detección de ciclo directo (Coach -> Orchestrator -> Coach con el mismo trace)
    msg_cycle = InterAgentMessage(
        source_agent="WellnessCoachAgent2.0",
        target_agent="OrchestratorAgent",
        user_id="u1",
        intent="REVERSE",
        trace_id=msg1.trace_id,
        hop_count=2
    )
    assert tracer.log_delegation(msg_cycle) is False, "Debe detectar el ciclo de delegación inversa"


def test_orchestrator_end_to_end_trace_logging():
    """Verifica que process_user_request incorpore trace_id e historial de delegación."""
    orch = OrchestratorAgent()
    res = orch.process_user_request("user_trace_test", "Tengo dolor de rodilla al hacer sentadilla")

    assert "trace_id" in res
    assert "task_id" in res
    assert "execution_time_ms" in res
    assert "trace_history" in res
    assert len(res["trace_history"]) >= 1
    assert res["trace_history"][0]["target_agent"] == "WellnessCoachAgent2.0"


def test_multidomain_trace_logging():
    """Verifica la trazabilidad en solicitudes compuestas multidominio."""
    orch = OrchestratorAgent()
    res = orch.process_user_request("user_multi_trace", "Rutina de piernas y plan de macronutrientes")

    assert res["intent"] == AgentIntent.MULTIDOMAIN.value
    assert len(res["trace_history"]) >= 3  # Multidomain + Coach + Nutrition


def test_communication_docs_integrity():
    """Verifica la existencia y contenido de la documentación de comunicación inter-agente y la nota MCP/A2A."""
    comm_doc = ROOT_DIR / "docs" / "agents" / "interagent-communication.md"
    mcp_note = ROOT_DIR / "docs" / "architecture" / "mcp-a2a-evolution-note.md"
    adr_008 = ROOT_DIR / "docs" / "architecture" / "adr" / "008-interagent-communication-protocol.md"

    assert comm_doc.exists()
    assert mcp_note.exists()
    assert adr_008.exists()

    comm_content = comm_doc.read_text(encoding="utf-8")
    assert "InterAgentMessage" in comm_content
    assert "DelegationTracer" in comm_content
    assert "```mermaid" in comm_content

    mcp_content = mcp_note.read_text(encoding="utf-8")
    assert "Model Context Protocol" in mcp_content
    assert "Agent-to-Agent" in mcp_content
