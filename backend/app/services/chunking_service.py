import nltk
from transformers import AutoTokenizer
import logging

# Configure Logging
logger = logging.getLogger(__name__)

class ChunkingService:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        # We use the same tokenizer as the model to ensure accurate token counts
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # BART max is 1024. We set limit lower to be safe and leave room for special tokens.
        self.max_chunk_tokens = 800 
        self.overlap_tokens = 150 

    def chunk_text(self, text: str):
        """
        Splits text into chunks with overlaps, respecting sentence boundaries.
        (Task 10 Implementation)
        """
        # 1. Split into natural sentences (Natural Breaking Points)
        sentences = nltk.sent_tokenize(text)
        
        chunks = []
        current_chunk_sents = []
        current_tokens = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            sent_tokens = len(self.tokenizer.encode(sentence, add_special_tokens=False))
            
            # Case A: A single sentence is huge (edge case)
            if sent_tokens > self.max_chunk_tokens:
                # If we have a current chunk, save it first
                if current_chunk_sents:
                    chunks.append(" ".join(current_chunk_sents))
                    current_chunk_sents = []
                    current_tokens = 0
                
                # Treat this long sentence as its own chunk (truncated if needed by model later)
                chunks.append(sentence)
                i += 1
                continue

            # Case B: Sentence fits in current chunk
            if current_tokens + sent_tokens <= self.max_chunk_tokens:
                current_chunk_sents.append(sentence)
                current_tokens += sent_tokens
                i += 1
            
            # Case C: Chunk is full -> Save & Create Overlap
            else:
                # Save current chunk
                chunks.append(" ".join(current_chunk_sents))
                
                # --- OVERLAP LOGIC ---
                # Backtrack to keep the last few sentences for the next chunk
                overlap_buffer = []
                overlap_len = 0
                backtrack_idx = i - 1
                
                while backtrack_idx >= 0:
                    prev_sent = sentences[backtrack_idx]
                    prev_len = len(self.tokenizer.encode(prev_sent, add_special_tokens=False))
                    
                    if overlap_len + prev_len <= self.overlap_tokens:
                        overlap_buffer.insert(0, prev_sent) # Prepend
                        overlap_len += prev_len
                        backtrack_idx -= 1
                    else:
                        break
                
                # Start new chunk with the overlap
                current_chunk_sents = overlap_buffer
                current_tokens = overlap_len
                # Loop continues to try adding the current sentence again
        
        # Add the last chunk
        if current_chunk_sents:
            chunks.append(" ".join(current_chunk_sents))
            
        logger.info(f"🧩 Smart Chunking: Split text into {len(chunks)} overlapping chunks.")
        return chunks

# Singleton Instance
chunker = ChunkingService()