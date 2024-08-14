from collections import namedtuple

Paragraph = namedtuple("Paragraph", ["index", "page", "line", "text"])


def document_metadata(document, **kwargs):
    metadata = {"uuid": document.uuid, "name": document.name}

    for key, value in kwargs.items():
        metadata[key] = value

    if document.path:
        metadata["path"] = document.path

    if document.url:
        metadata["url"] = document.url

    return metadata


def read_lines(path):
    with open(path, "r") as f:
        return (line.strip() for line in f.readlines())


def collect_paragraphs(lines, max_lines=30):
    result = []
    paragraph = []
    line = None

    for index, text in enumerate(lines):
        if not paragraph and not text:
            pass
        elif not text:
            content = " ".join(paragraph)
            paragraph = Paragraph(len(result), 0, line, content)
            result.append(paragraph)

            paragraph = []
            line = None
        elif len(paragraph) > max_lines:
            content = " ".join(paragraph)
            paragraph = Paragraph(len(result), 0, line, content)
            result.append(paragraph)

            paragraph = [text]
            line = index + 1
        else:
            line = index + 1 if line is None else line
            paragraph.append(text)

    if paragraph:
        content = " ".join(paragraph)
        paragraph = Paragraph(len(result), 0, line, content)
        result.append(paragraph)

    return result
