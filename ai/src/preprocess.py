"""
NEX-CIV: Text Preprocessing & Language Style Normalization
Handles:
1. Unicode NFC Normalization for Telugu script glyphs
2. Regex noise & URL cleaning while preserving Telugu Unicode (\u0c00-\u0c7f)
3. Zero-PII Sanitization (scrubs phone numbers, emails, door numbers)
4. Language Style Detection: 'te' (Pure Telugu), 'en' (English), 'te_latn' (Romanized Telugu)
"""

import re
import unicodedata
from typing import Dict, Any, Tuple

# Telugu Lexicon for Romanized Style Detection
TE_LATN_KEYWORDS = set([
    'veedhi', 'veedhilo', 'guntalu', 'paddayi', 'kallu', 'neeru', 'ravatledu',
    'ponguthondi', 'cheyandi', 'chala', 'motham', 'virigipoyi', 'ibbandi',
    'ninna', 'daggara', 'eduruga', 'undi', 'ayindi', 'kottukupoyindi',
    'chetha', 'kuppa', 'kullipoindi', 'padipoyindi', 'stambham', 'velagadam',
    'tagalekapotunnam', 'neellu', 'intloki', 'drainage', 'road', 'current'
])

TELUGU_STOPWORDS = set([
    'మా', 'ఈ', 'మరియు', 'వల్ల', 'కూడా', 'ఉంది', 'ఉన్నాయి', 'అని', 'ఒక',
    'వారి', 'ద్వారా', 'చేయండి', 'చేయాలి', 'వెంటనే', 'దగ్గర', 'వద్ద', 'లో', 'పై'
])

def sanitize_pii(text: str) -> str:
    """Removes potential personally identifiable information (phone numbers, emails, house numbers)."""
    if not isinstance(text, str):
        return ""
    # Remove 10-digit phone numbers
    text = re.sub(r'\b[6-9]\d{9}\b', '[REDACTED_PHONE]', text)
    # Remove emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    # Remove explicit house / door numbers e.g. D.No 12-34/A
    text = re.sub(r'(?:d\.?no\.?|h\.?no\.?|door\s*no\.?)\s*[:#-]?\s*[\w\/-]+', '[REDACTED_DOOR_NO]', text, flags=re.IGNORECASE)
    return text

def detect_language_style(text: str) -> str:
    """
    Detects language style:
    - 'te': Contains native Telugu Unicode characters (\u0c00-\u0c7f)
    - 'te_latn': Written in Latin script with Telugu phonetics/lexicon
    - 'en': Standard English civic text
    """
    if not isinstance(text, str):
        return 'en'
    
    # 1. Check for native Telugu Unicode
    if re.search(r'[\u0c00-\u0c7f]', text):
        return 'te'
    
    # 2. Check for Romanized Telugu lexical markers
    lower_words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    matches = sum(1 for w in lower_words if w in TE_LATN_KEYWORDS)
    if matches >= 1 and len(lower_words) > 0:
        if matches / len(lower_words) >= 0.10 or matches >= 2:
            return 'te_latn'
    
    return 'en'

def preprocess_complaint_text(
    text: str,
    strip_stopwords: bool = False,
    scrub_pii: bool = True
) -> Dict[str, Any]:
    """
    Complete preprocessing pipeline for civic complaints.
    Returns normalized text, detected language style, and sanitization flags.
    """
    if not isinstance(text, str):
        return {'cleaned_text': '', 'language_style': 'en', 'pii_scrubbed': False}

    # Step 1: Unicode NFC Normalization
    normalized = unicodedata.normalize('NFC', text.strip())

    # Step 2: Zero-PII Sanitization
    pii_scrubbed = False
    if scrub_pii:
        sanitized = sanitize_pii(normalized)
        if sanitized != normalized:
            pii_scrubbed = True
        normalized = sanitized

    # Step 3: URL removal
    cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', normalized)

    # Step 4: Language style detection before aggressive noise stripping
    lang_style = detect_language_style(cleaned)

    # Step 5: Clean punctuation while preserving Telugu Unicode range and alphanumeric characters
    cleaned = re.sub(r'[^\w\s\u0c00-\u0c7f]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Step 6: Optional stopword removal (mainly for classic TF-IDF, not transformer)
    if strip_stopwords:
        tokens = cleaned.split()
        if lang_style == 'te':
            tokens = [t for t in tokens if t not in TELUGU_STOPWORDS]
        cleaned = " ".join(tokens)

    return {
        'cleaned_text': cleaned,
        'original_text': text,
        'language_style': lang_style,
        'pii_scrubbed': pii_scrubbed
    }
