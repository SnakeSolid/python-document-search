from collections import namedtuple
from convert import convert_image, convert_text, convert_html, convert_pdf
from ollama import Message
from queue import Queue
from storage import download
from threading import Thread
import ollama

SourceDocument = namedtuple("SourceDocument",
                            ["uuid", "mimetype", "name", "path", "url"])


class Worker:

    def __init__(self, database):
        self.database = database
        self.queue = Queue()

    def add_path(self, uuid, mimetype, source_name, path):
        document = SourceDocument(uuid, mimetype, source_name, path, None)

        self.queue.put(document)

    def add_url(self, uuid, url):
        document = SourceDocument(uuid, None, None, None, url)

        self.queue.put(document)

    def start(self):
        thread = Thread(target=Worker.run,
                        args=[self.queue, self.database],
                        daemon=True)
        thread.start()

    def run(queue, database):
        while True:
            document = queue.get()

            if not document.url is None:
                mimetype, title, path = download(document.uuid, document.url)
                document = SourceDocument(document.uuid, mimetype, title, path,
                                          document.url)

            Worker.save(database, document)

    def save(database, document):
        if document.mimetype in ["application/pdf"]:
            Worker.save_pdf(database, document)
        elif document.mimetype in ["text/plain"]:
            Worker.save_text(database, document)
        elif document.mimetype in ["text/html"]:
            Worker.save_html(database, document)
        elif document.mimetype in ["image/png", "image/jpeg"]:
            Worker.save_image(database, document)
        else:
            print("Unsupported MIME type:", mimetype)

    def save_pdf(database, document):
        for fragment in convert_pdf(document):
            database.insert_fragment(fragment.id, fragment.embedding,
                                     fragment.metadata, fragment.text)

        database.insert_document(document.uuid,
                                 document.name,
                                 document.mimetype,
                                 path=document.path)

    def save_text(database, document):
        for fragment in convert_text(document):
            database.insert_fragment(fragment.id, fragment.embedding,
                                     fragment.metadata, fragment.text)

        database.insert_document(document.uuid,
                                 document.name,
                                 document.mimetype,
                                 path=document.path)

    def save_html(database, document):
        for fragment in convert_html(document):
            database.insert_fragment(fragment.id, fragment.embedding,
                                     fragment.metadata, fragment.text)

        database.insert_document(document.uuid,
                                 document.name,
                                 document.mimetype,
                                 path=document.path)

    def save_image(database, document):
        fragment = convert_image(document)
        database.insert_fragment(fragment.id, fragment.embedding,
                                 fragment.metadata, fragment.text)
        database.insert_document(document.uuid,
                                 document.name,
                                 document.mimetype,
                                 path=document.path)
