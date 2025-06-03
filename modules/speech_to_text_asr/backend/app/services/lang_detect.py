"""
Language Detection & Normalization Service (Module 03)

This stub provides:
 1. detect_language(text)       # "arabic", "english" or "franco-arabic"
 2. transliterate_franco(text)  # converts Franco-Arabic (latin+digits) to Arabic script
 3. normalize_text(text, lang)  # lowercasing, diacritics stripping, punctuation unification
 4. detect_and_normalize(text)  # combined helper

Place this file under:
  modules/03_Language_Detection_and_Normalization/lang_detect.py
"""
import re

# 1. Mapping for Franco-Arabic numeral/letter tokens → Arabic letters (digits and digraphs)
FRANCO_MAP = {
    "2": "أ",  # or ء
    "3": "ع",
    "5": "خ",
    "6": "ط",
    "7": "ح",
    "9": "ص",
    "th": "ث",
    "kh": "خ",
    "sh": "ش",
    # extend as needed
}

# 2. Letter-by-letter fallback mapping for Latin letters → Arabic
LETTER_MAP = {
    'a': 'ا', 'b': 'ب', 't': 'ت', 'g': 'ج', 'h': 'ه', 'd': 'د',
    'r': 'ر', 'z': 'ز', 's': 'س', 'k': 'ك', 'l': 'ل', 'm': 'م',
    'n': 'ن', 'y': 'ي', 'f': 'ف', 'q': 'ق', 'p': 'ب', 'o': 'و',
    'u': 'و', 'e': 'ي', 'i': 'ي', 'w': 'و', 'x': 'كس'
}

# -------- Language Detection --------
def detect_language(text: str) -> str:
    """
    Simple rule-based detection:
      - Arabic script → 'arabic'
      - Franco-Arabic numerals/digraphs → 'franco-arabic'
      - Otherwise → 'english'
    """
    if re.search(r"[\u0600-\u06FF]", text):
        return "arabic"
    if any(d in text for d in "235679") or any(dg in text.lower() for dg in ("th","sh","kh")):
        return "franco-arabic"
    return "english"

# -------- Transliteration --------
def transliterate_franco(text: str) -> str:
    """
    Convert Franco-Arabic (e.g. 'salam 3alaykom') to Arabic script.
    1. Handle digits and digraphs from FRANCO_MAP
    2. Map remaining Latin letters via LETTER_MAP
    """
    txt = text.lower()
    # 1. Replace token patterns (longest first)
    for token in sorted(FRANCO_MAP.keys(), key=len, reverse=True):
        arab = FRANCO_MAP[token]
        txt = re.sub(token, arab, txt)
    # 2. Map leftover letters
    result = []
    for ch in txt:
        if ch in LETTER_MAP:
            result.append(LETTER_MAP[ch])
        else:
            result.append(ch)  # keep spaces/punct
    return ''.join(result)

# -------- Normalization --------
def normalize_text(text: str, lang: str) -> str:
    """
    Normalize based on detected language:
     - English: lowercase, collapse repeated punctuation
     - Franco-Arabic: transliterate → then apply Arabic normalization
     - Arabic: strip diacritics, unify punctuation
    """
    if lang == "english":
        cleaned = text.lower().strip()
        cleaned = re.sub(r"([!?.,])\1+", r"\1", cleaned)
        return cleaned

    # For Franco-Arabic: transliterate first
    if lang == "franco-arabic":
        text = transliterate_franco(text)
    # Now treat as Arabic text
    cleaned = re.sub(r"[\u064B-\u0652]", "", text)            # remove diacritics
    cleaned = cleaned.replace(",", "،").replace("?", "؟")  # unify punctuation
    # Optional: normalize Alef/Ya variants
    # cleaned = cleaned.replace("إ", "ا").replace("أ", "ا").replace("آ", "ا").replace("ى", "ي")
    return cleaned.strip()

# -------- Combined Helper --------
def detect_and_normalize(text: str) -> dict:
    """
    Returns a dict:
      {
        "lang": "english"|"arabic"|"franco-arabic",
        "normalized_text": "..."
      }
    """
    lang = detect_language(text)
    normalized = normalize_text(text, lang)
    return {"lang": lang, "normalized_text": normalized}
