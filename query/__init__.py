from ollama import Message
from settings import MODEL_EMBEDDING
from collections import namedtuple
import ollama
import re

SOURSE_PATTERN = re.compile(r"\[\s*(#\d+(\s*,\s*#\d+)*)\s*\]")
INDEX_PATTERN = re.compile(r"#(\d+)")
LINK_FORMAT = "[[{name}]](#source_{index})"
SINGLE_SOURSE = """#{index}
```
{text}
```
"""
SUMMARIZE_PROMPT = """
{sources}

Answer the question `{query}` based on sources above. Give detailed answer in markdown format.

Add references to sources using source index in square brackets: [#1], [#2], [#3] etc.

Do not write introduction and conclusion only answer the question.

If sources does not contain answer answer "NOT_FOUND". Respond in {language} language.
"""

Response = namedtuple("Response", ["success", "text", "documents", "images"])


def _query_embedding(text):
    embedding = ollama.embeddings(MODEL_EMBEDDING, text)

    return embedding["embedding"]


def _format_sourse(index, text):
    return SINGLE_SOURSE.format(index=index, text=text.strip())


def _source_indexes(text):
    indexes = set()

    for references, _tail in SOURSE_PATTERN.findall(text):
        for index in INDEX_PATTERN.findall(references):
            indexes.add(int(index))

    return sorted(indexes)


def _normalize_indexes(matcher, mapping):
    text = matcher.group(0)
    indexes = sorted((int(index) for index in INDEX_PATTERN.findall(text)))
    links = (LINK_FORMAT.format(name=mapping[index], index=index)
             for index in indexes)

    return ", ".join(links)


def _normalize(text, mapping):
    return SOURSE_PATTERN.sub(lambda m: _normalize_indexes(m, mapping), text)


def _source_name(document):
    name = document["name"]

    for attribute in ["page", "paragraph", "line"]:
        if attribute in document:
            return "{} ({} {})".format(name, attribute, document[attribute])

    return name


def answer_query(database, query, language="English", n=20):
    embedding = _query_embedding(query)
    results = database.query(embedding, n)
    sources = "\n".join((_format_sourse(index, result["text"])
                         for index, result in enumerate(results)))
    prompt = SUMMARIZE_PROMPT.format(sources=sources,
                                     query=query,
                                     language=language)
    response = ollama.chat("gemma2",
                           messages=[Message(role="user", content=prompt)])
    content = response["message"]["content"].strip()

    if "NOT_FOUND" in content:
        return Response(False, None, None, None)

    documents = []
    images = []
    mapping = {}

    for index in _source_indexes(content):
        source = results[index]

        if "image" in source and source["image"]:
            images.append({
                "index": index,
                "uuid": source["uuid"],
                "name": _source_name(source),
            })
            mapping[index] = "image {}".format(len(images))
        else:
            documents.append({
                "index": index,
                "uuid": source["uuid"],
                "name": _source_name(source),
            })
            mapping[index] = "doc {}".format(len(documents))

    return Response(True, _normalize(content, mapping), documents, images)
