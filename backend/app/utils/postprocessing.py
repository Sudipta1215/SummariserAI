import re
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

# Ensure NLTK data is ready
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def clean_formatting(text: str) -> str:
    """
    Fixes capitalization, spacing, and punctuation.
    """
    if not text: return ""
    
    # 1. Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Fix spacing around punctuation (e.g., "word ,word" -> "word, word")
    text = re.sub(r'\s+([?.!,"])', r'\1', text)
    
    # 3. Capitalize first letter of every sentence
    sentences = sent_tokenize(text)
    capitalized = [s[0].upper() + s[1:] if len(s) > 1 else s for s in sentences]
    
    return " ".join(capitalized)

def remove_redundancy(text: str) -> str:
    """
    Detects and removes duplicate sentences (Simulated Sentence Reordering).
    """
    sentences = sent_tokenize(text)
    unique_sentences = []
    seen = set()
    
    for sent in sentences:
        # Create a simple hash/fingerprint for the sentence
        clean_sent = sent.lower().strip()
        if clean_sent not in seen:
            unique_sentences.append(sent)
            seen.add(clean_sent)
            
    return " ".join(unique_sentences)

def extract_local_keywords(text: str, num_keywords=5) -> str:
    """
    Extracts keywords using frequency analysis (No API key required).
    """
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Filter: Alphanumeric only, not in stop words, len > 2
    filtered_words = [
        w for w in words 
        if w.isalnum() and w not in stop_words and len(w) > 2
    ]
    
    # Get most common
    freq = Counter(filtered_words)
    common = freq.most_common(num_keywords)
    
    return ", ".join([word for word, count in common])