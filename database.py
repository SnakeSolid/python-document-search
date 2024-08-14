from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from collections import namedtuple
from settings import STORAGE_ROOT
import chromadb
import os
import sqlite3

CHROMADB_ROOT = os.path.join(STORAGE_ROOT, "embedding")
SQLITE_PATH = os.path.join(STORAGE_ROOT, "documents.sqlite")

INIT_DATABASE = """
CREATE TABLE IF NOT EXISTS documents (
    uuid TEXT NOT NULL,
    path TEXT,
    url TEXT,
    name TEXT NOT NULL,
    mimetype TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS documents_uuid ON documents(uuid);
"""

INSERT_DOCUMENT = """
INSERT INTO documents (
    uuid,
    path,
    url,
    name,
    mimetype)
VALUES (?, ?, ?, ?, ?)
"""

SELECT_DOCUMENT = """
SELECT
    uuid,
    path,
    url,
    name,
    mimetype
FROM documents
WHERE uuid = ?
"""

SELECT_DOCUMENTS = """
SELECT
    uuid,
    path,
    url,
    name,
    mimetype
FROM documents
"""

REMOVE_DOCUMENT = """
DELETE FROM documents
WHERE uuid = ?
"""

Document = namedtuple("Document", ["uuid", "path", "url", "name", "mimetype"])


class Database:

    def __init__(self):
        self.documents = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        self.documents.executescript(INIT_DATABASE)
        self.documents.commit()
        self.chromadb = chromadb.PersistentClient(
            path=CHROMADB_ROOT,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
        self.collection = self.chromadb.get_or_create_collection(
            name="documents")

    def insert_document(self, uuid, filename, mimetype, path=None, url=None):
        self.documents.execute(INSERT_DOCUMENT,
                               (uuid, path, url, filename, mimetype))
        self.documents.commit()

    def select_document(self, uuid):
        row = self.documents.execute(SELECT_DOCUMENT, (uuid, )).fetchone()

        if row is None:
            return None

        return Document(row[0], row[1], row[2], row[3], row[4])

    def select_documents(self):
        return [
            Document(uuid, path, url, name, mimetype)
            for uuid, path, url, name, mimetype in self.documents.execute(
                SELECT_DOCUMENTS).fetchall()
        ]

    def remove_document(self, uuid):
        self.collection.delete(where={"uuid": uuid})
        self.documents.execute(REMOVE_DOCUMENT, (uuid, )).fetchall()
        self.documents.commit()

    def insert_fragment(self, uuid, embedding, metadata, document):
        self.collection.add(
            ids=[uuid],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document],
        )

    def query(self, embedding, n=20):
        documents = self.collection.query(
            query_embeddings=[embedding],
            n_results=n,
            include=["metadatas", "documents", "distances"])
        ids = documents["ids"][0]
        metadatas = documents["metadatas"][0]
        documents = documents["documents"][0]
        results = []

        for index in range(len(ids)):
            row = {"text": documents[index], **metadatas[index]}

            results.append(row)

        return results
