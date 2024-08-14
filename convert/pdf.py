from .core import document_metadata, read_lines, collect_paragraphs
from collections import defaultdict
from collections import namedtuple
from ollama import Message
from pypdf import PdfReader
from settings import MODEL_EMBEDDING
from settings import MODEL_IMAGE
import ollama

FIX_TEXT_PROMPT = """
```
{text}
```

Fix this text. Keep language and style, change only format and fix syntax errors. Do not write any introduction and conclusion.
"""

PageLines = namedtuple("PageLines", ["index", "lines"])
PageText = namedtuple("PageText", ["index", "text"])
Fragment = namedtuple("Fragment", ["id", "text", "embedding", "metadata"])


def extract_pages(path):
    pages = []

    with PdfReader(path) as reader:
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            lines = text.splitlines()
            page = PageLines(index, lines)
            pages.append(page)

    return pages


def collect_watermarks(pages):
    frequence = defaultdict(int)
    n_pages = len(pages)

    for _, lines in pages:
        for line in lines:
            frequence[line] += 1

    watermarks = set(
        (line for line, count in frequence.items() if count > n_pages / 2))

    return watermarks


def remove_watermarks(pages):
    watermarks = collect_watermarks(pages)
    result = []

    for index, lines in pages:
        lines = [line for line in lines if not line in watermarks]

        if not lines:
            continue

        page = PageLines(index, lines)
        result.append(page)

    return result


def fix_text_style(pages):
    result = []

    for index, lines in pages:
        text = " ".join(lines)
        prompt = FIX_TEXT_PROMPT.format(text=text)
        response = ollama.chat(MODEL_TEXT,
                               messages=[Message(role="user", content=prompt)])
        content = response["message"]["content"]
        page = PageText(index, content.strip())
        result.append(page)

    return result


def convert_pdf(document):
    all_pages = extract_pages(document.path)
    clean_pages = remove_watermarks(all_pages)
    fixed_pages = fix_text_style(clean_pages)
    fragments = []

    for index, text in fixed_pages:
        fragment_id = "{}:{}".format(document.uuid, index)
        embedding = ollama.embeddings(MODEL_EMBEDDING, text)
        metadata = document_metadata(document, page=index)
        fragment = Fragment(fragment_id, text, embedding["embedding"],
                            metadata)
        fragments.append(fragment)

    return fragments
