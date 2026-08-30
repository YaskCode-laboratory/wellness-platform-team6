"""
Suite de Pruebas Unitarias e Integración para la Generación de Embeddings (Issue #7 - S1-03).
Verifica dimensionalidad, consistencia vectorial, norma L2, búsqueda semántica y estructura del Vector Store.
"""

import json
import math
import sys
from pathlib import Path

import pytest

# Agregar src/backend a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.embeddings_generator import EmbeddingsGenerator, cosine_similarity


@pytest.fixture
def generator():
    return EmbeddingsGenerator(model_name="sentence-transformers/all-MiniLM-L6-v2", vector_dim=384)


def test_embedding_dimensionality(generator):
    """Verifica que el vector generado tenga exactamente 384 dimensiones."""
    text = "Sentadilla libre con barra y técnica de alineación articular neutra."
    emb_data = generator.generate_embedding(text)

    assert emb_data["dimension"] == 384
    assert len(emb_data["vector"]) == 384
    assert isinstance(emb_data["vector"], list)


def test_embedding_l2_normalization(generator):
    """Verifica que la norma L2 del vector generado sea aproximadamente 1.0 (vector unitario)."""
    text = "Hipertrofia muscular y sobrecarga progresiva."
    emb_data = generator.generate_embedding(text)
    vector = emb_data["vector"]

    norm = math.sqrt(sum(x * x for x in vector))
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_empty_text_embedding(generator):
    """Verifica el comportamiento seguro al procesar cadenas vacías."""
    emb_data = generator.generate_embedding("")

    assert emb_data["dimension"] == 384
    assert len(emb_data["vector"]) == 384
    assert all(x == 0.0 for x in emb_data["vector"])


def test_cosine_similarity_identical_vectors():
    """Verifica que la similitud coseno de vectores idénticos sea 1.0."""
    vec_a = [0.6, 0.8, 0.0]
    vec_b = [0.6, 0.8, 0.0]
    sim = cosine_similarity(vec_a, vec_b)
    assert pytest.approx(sim, rel=1e-3) == 1.0


def test_semantic_similarity_relevance(generator):
    """Verifica que una consulta médica coincida mejor con el chunk de hernia discal que con uno ortogonal."""
    query = "Hernia discal lumbar y ejercicios prohibidos"
    chunk_hernia = "### Contexto: 2. Matriz de Sustitución\nHernia Discal L4-L5 Lumbar contraindica Sentadilla Libre con Barra."
    chunk_hipertrofia = "### Contexto: 3. Periodización\nFase de Hipertrofia: Rangos de 6 a 12 repeticiones."

    vec_query = generator.generate_embedding(query)["vector"]
    vec_hernia = generator.generate_embedding(chunk_hernia)["vector"]
    vec_hipertrofia = generator.generate_embedding(chunk_hipertrofia)["vector"]

    sim_hernia = cosine_similarity(vec_query, vec_hernia)
    sim_hipertrofia = cosine_similarity(vec_query, vec_hipertrofia)

    assert sim_hernia > sim_hipertrofia


def test_vector_store_file_integrity():
    """Verifica la existencia y esquema JSON del archivo data/vector_store/embeddings.json."""
    vector_store_file = ROOT_DIR / "data" / "vector_store" / "embeddings.json"
    assert vector_store_file.exists(), "El archivo data/vector_store/embeddings.json debe existir"

    with open(vector_store_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert "vectors" in data
    assert data["metadata"]["total_chunks"] == len(data["vectors"])
    assert data["metadata"]["vector_dimension"] == 384

    for item in data["vectors"]:
        assert "chunk_id" in item
        assert "source_file" in item
        assert "text" in item
        assert "vector" in item
        assert len(item["vector"]) == 384
