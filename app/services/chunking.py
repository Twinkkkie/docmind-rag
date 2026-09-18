def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        piece = cleaned[start:end]

        if end < len(cleaned):
            boundary = piece.rfind(" ")
            if boundary >= chunk_size // 2:
                end = start + boundary
                piece = cleaned[start:end]

        chunks.append(piece.strip())
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)

    return [chunk for chunk in chunks if chunk]
