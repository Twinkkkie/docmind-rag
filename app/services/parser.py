from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class UnsupportedDocumentError(ValueError):
    pass


def extract_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

    if suffix in {".txt", ".md", ".markdown"}:
        return data.decode("utf-8", errors="replace").strip()

    raise UnsupportedDocumentError("Only PDF, TXT and Markdown files are supported.")
