"""
Módulo RAG Chunker — Wellness Lift
Implementa la estrategia de segmentación semántica basada en Markdown con ventana deslizante (Sliding Window)
para la generación de embeddings y recuperación en el motor RAG.
"""

import os
import json
import re
from typing import List, Dict, Any

class MarkdownSemanticChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        """
        Inicializa el segmentador RAG.
        :param chunk_size: Tamaño objetivo del chunk en tokens/palabras estáticas (~512).
        :param chunk_overlap: Solapamiento entre chunks adyacentes (~64 tokens).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _estimate_tokens(self, text: str) -> int:
        """Estimación aproximada de tokens basada en conteo de palabras e intervalos."""
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
        """Aplica la ventana deslizante sobre secciones para respetar chunk_size y chunk_overlap."""
        heading = section["heading"]
        content = section["content"]
        tokens = self._estimate_tokens(content)

        chunks = []

        if tokens <= self.chunk_size:
            if content.strip():
                chunks.append({
                    "chunk_id": f"{source_file}#{heading.lower().replace(' ', '_')}-0",
                    "source_file": source_file,
                    "heading_context": heading,
                    "token_count": tokens,
                    "text": f"### Contexto: {heading}\n{content}"
                })
        else:
            # Ventana deslizante para contenidos extensos
            words = content.split()
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
                    "token_count": len(chunk_words),
                    "text": f"### Contexto: {heading} (Parte {sub_id + 1})\n{chunk_text}"
                })

                sub_id += 1
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
    print("Módulo rag_chunker inicializado correctamente.")
