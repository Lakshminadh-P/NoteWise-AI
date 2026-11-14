"""
PDF text extraction service using PyMuPDF.
"""

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """
    Extract all text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Tuple of (extracted_text, page_count).
    """
    doc = fitz.open(file_path)
    pages_text = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text("text")
        if text.strip():
            pages_text.append(f"[Page {page_num}]\n{text}")

    page_count = len(doc)
    doc.close()

    full_text = "\n\n".join(pages_text)
    return full_text, page_count


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for LLM processing.

    Args:
        text: The full extracted text.
        chunk_size: Maximum characters per chunk.
        overlap: Characters of overlap between chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at a paragraph or sentence boundary
        if end < len(text):
            last_para = chunk.rfind("\n\n")
            last_sentence = chunk.rfind(". ")
            break_point = max(last_para, last_sentence)
            if break_point > chunk_size * 0.5:
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks
