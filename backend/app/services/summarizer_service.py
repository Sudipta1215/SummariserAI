import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import logging
import re
from app.services.chunking_service import chunker 
# Ensure you have this file created from the previous step
from app.utils.postprocessing import clean_formatting, remove_redundancy, extract_local_keywords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SummarizerService, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        self.model_name = "facebook/bart-large-cnn"
        logger.info(f"⏳ Loading Local Model: {self.model_name}...")
        
        if torch.cuda.is_available(): self.device = 0 
        else: self.device = -1 
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.pipeline = pipeline(
                "summarization", model=self.model, tokenizer=self.tokenizer, device=self.device
            )
            logger.info("✅ Local Model Loaded!")
        except Exception as e:
            logger.error(f"❌ Model Load Failed: {e}")
            raise e

    def _get_params(self, length_option="medium", detail_level="standard"):
        """
        Maps UI options to Model Constraints (Tokens).
        """
        # Base constraints
        base_map = {
            "short": {"max": 150, "min": 30},
            "medium": {"max": 300, "min": 60},
            "long": {"max": 600, "min": 150}
        }
        
        params = base_map.get(length_option.lower(), base_map["medium"])
        
        # Adjust based on Detail Level
        if detail_level.lower() == "detailed":
            params["min"] += 50  # Force it to be longer/more detailed
        elif detail_level.lower() == "concise":
            params["max"] -= 30  # Force it to be tighter

        return params

    def apply_style(self, text, style):
        """
        Manually converts paragraph text to bullet points if requested.
        """
        if not text: return ""
        
        # Clean up text first
        text = text.replace(" .", ".")
        
        if style == "Bullet Points":
            # Split by sentences (simple heuristic)
            sentences = re.split(r'(?<=[.!?]) +', text)
            # Create bullets
            bullets = [f"• {s.strip()}" for s in sentences if len(s.strip()) > 5]
            return "\n".join(bullets)
        
        # Default: Paragraph
        return text

    def summarize_chunk(self, text, params):
        # Calculate safe max length based on input size
        input_len = len(self.tokenizer.encode(text))
        
        # Safety: Output can't be larger than input
        safe_max = min(params['max'], int(input_len * 0.7))
        safe_min = min(params['min'], safe_max - 5)
        
        if safe_max < 10: return "" # Too short to summarize

        try:
            res = self.pipeline(
                text, 
                max_length=safe_max, 
                min_length=safe_min, 
                truncation=True,
                num_beams=4,
                do_sample=False
            )
            return res[0]['summary_text']
        except:
            return ""

    def generate_summary(self, raw_text: str, length_option="medium", style="Paragraph", detail="Standard") -> dict:
        """
        Main Function: Chunk -> Summarize -> Post-Process -> Style -> Return
        """
        # 1. Chunking
        chunks = chunker.chunk_text(raw_text)
        logger.info(f"📚 Processing {len(chunks)} chunks locally...")
        
        # 2. Constraints
        params = self._get_params(length_option, detail)
        
        # 3. Summarize
        partial_summaries = []
        for chunk in chunks:
            s = self.summarize_chunk(chunk, params)
            if s: partial_summaries.append(s)
            
        # 4. Join
        combined_text = " ".join(partial_summaries)
        
        # --- TASK 12: POST-PROCESSING ---
        # A. Remove Duplicates
        polished_text = remove_redundancy(combined_text)
        
        # B. Formatting
        polished_text = clean_formatting(polished_text)
        
        # C. Apply Bullet Points (This is where the style happens!)
        final_output = self.apply_style(polished_text, style)
        
        # D. Extract Keywords locally
        keywords = extract_local_keywords(final_output)
        
        return {
            "summary_text": final_output,
            "keywords": keywords
        }

summarizer_service = SummarizerService()