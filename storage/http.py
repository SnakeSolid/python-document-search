from settings import DOCUMENT_ROOT
import html
import mimetypes
import os
import re
import requests

FILE_NAME_PATTERN = re.compile("""filename="([^"]+)""", re.IGNORECASE)


def save(document_id, file):
    mimetype = file.mimetype
    extension = mimetypes.guess_extension(mimetype)
    filename = "{}{}".format(document_id, extension)
    path = os.path.join(DOCUMENT_ROOT, filename)
    file.save(path)

    return path


def _get_mimetype(headers):
    content_type = headers.get("Content-Type")
    mimetype = content_type.split(";")[0].strip()

    return mimetype


def _get_filename(headers):
    disposition = headers.get('Content-Disposition')

    if disposition:
        matcher = FILE_NAME_PATTERN.search(disposition)

        if matcher:
            return matcher.group(1)

    return None


def _get_title(content):
    start = content.find(b"<title>")

    if start == -1:
        return None

    end = content.find(b"</title>", start)

    if start == -1:
        return None

    return html.unescape(content[start + 7:end].decode("utf8"))


def download(document_id, uri):
    response = requests.get(uri)
    mimetype = _get_mimetype(response.headers)
    extension = mimetypes.guess_extension(mimetype)
    filename = "{}{}".format(document_id, extension)
    path = os.path.join(DOCUMENT_ROOT, filename)
    title = _get_filename(response.headers) or _get_title(
        response.content) or uri

    with open(path, "wb") as f:
        f.write(response.content)

    return mimetype, title, path
