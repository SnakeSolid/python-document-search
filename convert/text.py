from .core import document_metadata, read_lines, collect_paragraphs
from collections import namedtuple
from ollama import Message
from settings import MODEL_EMBEDDING
import ollama

Fragment = namedtuple("Fragment", ["id", "text", "embedding", "metadata"])


def convert_text(document):
    fragments = []

    for paragraph in collect_paragraphs(read_lines(document.path)):
        fragment_id = "{}:{}".format(document.uuid, paragraph.line)
        embedding = ollama.embeddings(MODEL_EMBEDDING, paragraph.text)
        metadata = document_metadata(document, line=paragraph.line)
        fragment = Fragment(fragment_id, paragraph.text,
                            embedding["embedding"], metadata)
        fragments.append(fragment)

    return fragments
