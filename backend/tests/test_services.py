from app.services.book_service import book_service

def test_text_chunking():
    long_text = "word " * 1000  # 1000 words
    chunks = book_service.chunk_text(long_text, chunk_size=500)
    
    assert len(chunks) > 0
    
    # ✅ FIX: Split by space to count WORDS, not characters
    first_chunk_word_count = len(chunks[0].split())
    assert first_chunk_word_count <= 500
    print("✅ Chunking logic works")