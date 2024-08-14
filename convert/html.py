from .core import document_metadata
from collections import namedtuple
from ollama import Message
from settings import MODEL_EMBEDDING
from trafilatura import fetch_url, bare_extraction
from trafilatura.xml import xmltotxt
import ollama

Fragment = namedtuple("Fragment", ["id", "text", "embedding", "metadata"])


def convert_html(document):
    with open(document.path, "r") as f:
        content = f.read()

    content = bare_extraction(content,
                              include_formatting=True,
                              with_metadata=True,
                              as_dict=False)
    fragments = []

    for index, element in enumerate(content.body):
        text = xmltotxt(element, include_formatting=True)
        fragment_id = "{}:{}".format(document.uuid, index)
        embedding = ollama.embeddings(MODEL_EMBEDDING, text)
        metadata = document_metadata(document, paragraph=index)
        fragment = Fragment(fragment_id, text, embedding["embedding"],
                            metadata)
        fragments.append(fragment)

    return fragments
