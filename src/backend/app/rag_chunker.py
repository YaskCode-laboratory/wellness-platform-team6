"""
Módulo RAG Chunker — Wellness Lift (Issue #6 - S1-02).
Implementa la estrategia de segmentación semántica basada en Markdown con ventana deslizante (Sliding Window)
y solapamiento (Overlap) a nivel de palabras (con estimación de tokens) para la ingesta del motor RAG.
"""

import os
import json
import re
from typing import List, Dict, Any


class MarkdownSemanticChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        """
        Inicializa el segmentador RAG.
        :param chunk_size: Tamaño máximo del chunk en palabras (~512 palabras, equivalentes a ~650-700 tokens estimados).
        :param chunk_overlap: Solapamiento entre chunks adyacentes en palabras (~64 palabras, equivalentes a ~80-90 tokens estimados).
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap debe ser menor que chunk_size para permitir el avance de la ventana.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _estimate_tokens(self, text: str) -> int:
        """Estimación aproximada de tokens basada en conteo de palabras y signos ortográficos."""
        return len(re.findall(r'\w+|\S', text))

    def split_markdown_by_headings(self, text: str) -> List[Dict[str, str]]:
        """Segmentación primaria por estructura jerárquica Markdown (#, ##, ###)."""
        sections = []
        current_heading = "Introducción General"
        current_lines = []

        for line in text.splitlines():
            if line.startswith('#'):
                if current_lines:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_lines).strip()
                    })
                    current_lines = []
                current_heading = line.lstrip('#').strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_lines).strip()
            })

        return sections

    def chunk_section(self, section: Dict[str, str], source_file: str) -> List[Dict[str, Any]]:
        """
        Aplica segmentación y ventana deslizante con solapamiento sobre secciones Markdown.
        Si la sección excede chunk_size palabras, se divide en chunks consecutivos con chunk_overlap palabras comunes.
        """
        heading = section["heading"]
        content = section["content"].strip()
        if not content:
            return []

        words = content.split()
        chunks = []

        if len(words) <= self.chunk_size:
            chunks.append({
                "chunk_id": f"{source_file}#{heading.lower().replace(' ', '_')}-0",
                "source_file": source_file,
                "heading_context": heading,
                "word_count": len(words),
                "token_count": self._estimate_tokens(content),
                "text": f"### Contexto: {heading}\n{content}"
            })
        else:
            # Ventana deslizante para secciones extensas (> chunk_size palabras)
            start = 0
            sub_id = 0
            while start < len(words):
                end = min(start + self.chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)

                chunks.append({
                    "chunk_id": f"{source_file}#{heading.lower().replace(' ', '_')}-{sub_id}",
                    "source_file": source_file,
                    "heading_context": heading,
                    "word_count": len(chunk_words),
                    "token_count": self._estimate_tokens(chunk_text),
                    "text": f"### Contexto: {heading} (Parte {sub_id + 1})\n{chunk_text}"
                })

                sub_id += 1
                if end == len(words):
                    break
                start += (self.chunk_size - self.chunk_overlap)

        return chunks

    def process_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Procesa un archivo Markdown completo y retorna la lista de chunks estructurados."""
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        sections = self.split_markdown_by_headings(text)
        all_chunks = []
        for sec in sections:
            all_chunks.extend(self.chunk_section(sec, filename))

        return all_chunks


if __name__ == "__main__":
    chunker = MarkdownSemanticChunker(chunk_size=512, chunk_overlap=64)
    print("Módulo rag_chunker inicializado y configurado a nivel de palabras con estimación de tokens.")
