from .core import document_metadata, read_lines, collect_paragraphs
from collections import namedtuple
from ollama import Message
from settings import MODEL_TRANSLATE
import ollama

TRANSLATE_PROMPT = """
```
{text}
```

Translate this text into English. Keep text style. Do not write any introduction and conclusion.
"""

Translate = namedtuple("Translate", ["changed", "result", "source"])


def _is_english(text):
    n_ascii = sum((1 for ch in text if ch.isalpha() and ch.isascii()))
    n_letters = sum((1 for ch in text if ch.isalpha()))

    # Assume that English letters can appear in normal text.
    return n_ascii < 10 * n_letters


def translate(text):
    if _is_english(text):
        prompt = TRANSLATE_PROMPT.format(text=text)
        response = ollama.chat(MODEL_TRANSLATE,
                               messages=[Message(role="user", content=prompt)])
        content = response["message"]["content"].strip()

        return Translate(True, content, text)

    return Translate(False, text, text)
