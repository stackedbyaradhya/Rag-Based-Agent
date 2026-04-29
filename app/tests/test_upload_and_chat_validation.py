from app.services.chunk_service import ChunkService


def test_chunking_returns_multiple_chunks() -> None:
    text = "A" * 2500
    chunks = ChunkService.chunk_text(text)
    assert len(chunks) >= 2


def test_chunk_cleaning_normalizes_whitespace() -> None:
    cleaned = ChunkService.clean_text("hello   world\n\nfrom\tteam")
    assert cleaned == "hello world from team"
