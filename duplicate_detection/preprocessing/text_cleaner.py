import re
import unicodedata
from typing import Dict, Any, Tuple

# Unicode range for Telugu script: \u0C00 - \u0C7F
TELUGU_RANGE = re.compile(r'[\u0C00-\u0C7F]')

# Common Telugu stopwords and filler words in grievance submissions
TELUGU_FILLERS = {
    'గారు', 'అయ్యా', 'సార్', 'నమస్కారం', 'దయచేసి', 'వెంటనే', 'మా', 'మాకు',
    'ఇక్కడ', 'వలన', 'చాలా', 'ఉంది', 'ఉన్నాయి', 'లేదు', 'రావడం'
}

def detect_language(text: str) -> str:
    """
    Detects complaint language style:
    - 'te': Pure Telugu (native Telugu script)
    - 'te_latn': Romanized Telugu (Telugu spoken language transliterated into English script)
    - 'en': Pure English
    """
    if not text or not isinstance(text, str):
        return 'en'
    
    # Check for presence of Telugu unicode characters
    telugu_chars = len(TELUGU_RANGE.findall(text))
    total_chars = len(re.sub(r'\s+', '', text))
    
    if total_chars == 0:
        return 'en'
    
    if (telugu_chars / total_chars) > 0.25:
        return 'te'
    
    # Distinguish Romanized Telugu from English
    text_lower = text.lower()
    romanized_markers = [
        'veedhilo', 'colony lo', 'ravatledu', 'pani cheyadam ledu', 'ponguthondi',
        'chala samasya', 'karanam ga', 'thondaraga', 'baga', 'undhi', 'chesukondi',
        'dhayachesi', 'ippude', 'neellu', 'chetha', 'kaluva', 'gundalu', 'velagadam'
    ]
    if any(marker in text_lower for marker in romanized_markers):
        return 'te_latn'
        
    return 'en'


def normalize_telugu_text(text: str) -> str:
    """
    Normalizes Telugu text:
    - NFC Unicode normalization
    - Removes zero-width joiners / non-joiners (\u200C, \u200D) where safe
    - Normalizes punctuation and multiple spaces
    - Preserves Telugu vowel signs (Matras) and Virama (\u0C4D)
    """
    if not text:
        return ""
    
    # NFC normalization standardizes composite characters
    text = unicodedata.normalize('NFC', text)
    
    # Replace non-breaking spaces and special zero-widths
    text = text.replace('\u00A0', ' ').replace('\u200b', '')
    
    # Normalize excessive punctuation but keep sentence boundaries
    text = re.sub(r'[!?,:;]+', ' ', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def clean_complaint_text(text: str) -> Tuple[str, str]:
    """
    Cleans complaint description while preserving original semantic intent and detecting language.
    Returns: (cleaned_text, language_code)
    """
    if not text:
        return "", "en"
    
    raw = str(text).strip()
    lang = detect_language(raw)
    normalized = normalize_telugu_text(raw)
    
    return normalized, lang
