from .core import document_metadata
from collections import namedtuple
from ollama import Message
from settings import MODEL_EMBEDDING
from settings import MODEL_IMAGE
import ollama

Fragment = namedtuple("Fragment", ["id", "text", "embedding", "metadata"])


def convert_image(document):
    response = ollama.chat(
        MODEL_IMAGE, messages=[Message(role="user", images=[document.path])])
    content = response["message"]["content"]
    embedding = ollama.embeddings(MODEL_EMBEDDING, content)
    metadata = document_metadata(document, image=True)

    return Fragment(document.uuid, content, embedding["embedding"], metadata)
