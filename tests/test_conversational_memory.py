"""
Suite de Pruebas Automatizadas para Memoria Conversacional (Issue #14 - S2-03).
Verifica la memoria a corto plazo, persistencia a largo plazo, extracción de hechos y contexto multi-turno.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app import agent
from app.wellness_agent.memory import ConversationMemoryManager


@pytest.fixture
def memory_manager(tmp_path):
    """Fixture que crea una instancia de ConversationMemoryManager usando un directorio temporal."""
    return ConversationMemoryManager(max_history_turns=3, storage_dir=tmp_path)


def test_short_term_buffer_truncation(memory_manager):
    """Verifica que la ventana de memoria a corto plazo se tranque al exceder max_history_turns * 2."""
    user_id = "test_user_truncation"

    for i in range(10):
        memory_manager.add_message(user_id, "user", f"Mensaje usuario {i}")
        memory_manager.add_message(user_id, "assistant", f"Respuesta asistente {i}")

    history = memory_manager.get_history(user_id)
    assert len(history) == 6
    assert history[0]["content"] == "Mensaje usuario 7"
    assert history[-1]["content"] == "Respuesta asistente 9"


def test_fact_extraction(memory_manager):
    """Verifica que la memoria extraiga automáticamente hechos clave como condiciones físicas o récords."""
    user_id = "test_user_facts"

    memory_manager.add_message(user_id, "user", "Hola, últimamente me duele mucho la zona lumbar.")
    memory_manager.add_message(user_id, "user", "Ayer hice press de banca y mi máximo fue 85 kg.")

    facts = memory_manager.get_extracted_facts(user_id)
    assert len(facts) >= 2
    assert any("lumbar" in f.lower() for f in facts)
    assert any("85 kg" in f.lower() for f in facts)


def test_long_term_persistence(memory_manager, tmp_path):
    """Verifica guardar y cargar memoria conversacional y hechos desde el almacenamiento persistente."""
    user_id = "test_user_persistence"

    memory_manager.add_message(user_id, "user", "Tengo molestias en la rodilla izquierda.")
    memory_manager.add_message(user_id, "assistant", "Entendido, omitiremos flexiones profundas.")

    new_manager = ConversationMemoryManager(storage_dir=tmp_path)
    loaded = new_manager.load_from_persistence(user_id)

    assert loaded is True
    history = new_manager.get_history(user_id)
    facts = new_manager.get_extracted_facts(user_id)

    assert len(history) == 2
    assert len(facts) >= 1
    assert "rodilla" in facts[0].lower()


def test_new_session_auto_loads_and_preserves_history(tmp_path):
    """
    Simula: sesión 1 -> guardar -> nueva instancia -> nuevo mensaje -> recuperar contexto anterior
    y verifica que la información previa y el historial completo se conservan.
    """
    user_id = "test_user_session_flow"

    # Sesión 1: Instancia inicial de memoria
    manager_s1 = ConversationMemoryManager(storage_dir=tmp_path)
    manager_s1.add_message(user_id, "user", "Hola, me molesta la zona lumbar.")
    manager_s1.add_message(user_id, "assistant", "Entendido, adaptaremos tu entrenamiento.")

    # Sesión 2: Nueva instancia de ConversationMemoryManager (simulando nuevo proceso/sesión)
    manager_s2 = ConversationMemoryManager(storage_dir=tmp_path)
    # add_message debe cargar automáticamente la memoria previa sin sobrescribirla
    manager_s2.add_message(user_id, "user", "¿Qué rutina me sugieres para hoy?")

    full_history = manager_s2.get_full_history(user_id)
    facts = manager_s2.get_extracted_facts(user_id)

    # Verificar que la historia completa contiene los 3 mensajes en secuencia
    assert len(full_history) == 3
    assert full_history[0]["content"] == "Hola, me molesta la zona lumbar."
    assert full_history[1]["content"] == "Entendido, adaptaremos tu entrenamiento."
    assert full_history[2]["content"] == "¿Qué rutina me sugieres para hoy?"

    # Verificar que el hecho extraído en la Sesión 1 se mantiene
    assert any("lumbar" in f.lower() for f in facts)

    manager_s2.clear_memory(user_id)


def test_full_long_term_history_preservation_beyond_short_term_buffer(tmp_path):
    """Verifica que el historial completo a largo plazo se guarde en JSON sin ser truncado por el buffer a corto plazo."""
    user_id = "test_user_long_term"
    manager = ConversationMemoryManager(max_history_turns=3, storage_dir=tmp_path)

    # Agregar 10 turnos (20 mensajes)
    for i in range(10):
        manager.add_message(user_id, "user", f"Mensaje usuario {i}")
        manager.add_message(user_id, "assistant", f"Respuesta asistente {i}")

    # El buffer de corto plazo debe retornar los últimos 6 mensajes (3 turnos)
    short_term = manager.get_history(user_id)
    assert len(short_term) == 6

    # La memoria completa de largo plazo debe conservar los 20 mensajes completos
    full_history = manager.get_full_history(user_id)
    assert len(full_history) == 20
    assert full_history[0]["content"] == "Mensaje usuario 0"
    assert full_history[-1]["content"] == "Respuesta asistente 9"

    manager.clear_memory(user_id)


def test_multi_turn_dialogue_agent_integration(tmp_path):
    """Verifica que las respuestas e información previa influyan en los turnos posteriores del agente."""
    user_id = "test_user_multiturn"
    agent_memory = ConversationMemoryManager(storage_dir=tmp_path)
    agent.memory_manager = agent_memory
    agent._agent_instance.memory = agent_memory

    # Turno 1: Usuario declara hernia discal en el chat
    agent_memory.add_message(user_id, "user", "Hola, sufro de hernia discal lumbar L4-L5.")
    facts = agent_memory.get_extracted_facts(user_id)
    assert any("lumbar" in f.lower() or "hernia" in f.lower() for f in facts)

    # Turno 2: Generar rutina influenciada por el hecho guardado
    routine = agent._generate_local_routine(user_id)
    assert "weekly_schedule" in routine

    # La sentadilla libre con barra debe ser excluida por la regla biomecánica de la hernia discal
    all_exercise_names = [
        ex["name"]
        for day in routine["weekly_schedule"]
        for ex in day.get("exercises", [])
    ]
    assert not any("Sentadilla con Barra" in name for name in all_exercise_names)

    agent_memory.clear_memory(user_id)

