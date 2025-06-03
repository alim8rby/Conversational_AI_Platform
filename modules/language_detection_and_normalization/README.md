Module 03: Language Detection & Normalization

This module takes raw text (from ASR) and:

Detects its language category:

english (Latin letters)

arabic (Arabic script)

franco-arabic (Latin letters + digits spelling Arabic words)

Normalizes the text:

English: lowercasing, collapsing repeated punctuation

Arabic: stripping diacritics, unifying punctuation

Franco-Arabic: transliterating digits/digraphs to Arabic script, then applying Arabic normalization

📦 File Structure

modules/
└── 03_Language_Detection_and_Normalization/
    ├── __init__.py
    ├── lang_detect.py    # detection & normalization logic
    └── README.md         # this file

🚀 How to Run

Ensure your Flask server (with lang_detect.py imported) is running.

Send a POST request to /normalize:

curl -X POST http://127.0.0.1:5000/normalize \
  -H "Content-Type: application/json" \
  -d '{"text":"salam 3alaykom"}'

You should receive a JSON response with real Arabic characters:

{
  "lang": "franco-arabic",
  "normalized_text": "سلام عليكم"
}

Try more examples:

English: curl ... -d '{"text":"Hello!!!"}'  → {"lang":"english","normalized_text":"hello!"}

Arabic: curl ... -d '{"text":"مرحبا؟؟"}' → {"lang":"arabic","normalized_text":"مرحبا؟"}