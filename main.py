from collections import namedtuple
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from query import answer_query
from settings import LANGUAGES
from storage import Database
from storage import save
from storage import Worker
import os
import uuid

app = Flask(__name__, template_folder="templates")
database = Database()
worker = Worker(database)


@app.route("/")
def index():
    return render_template("search.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/documents")
def documents():
    return render_template("documents.html")


@app.route('/static/<path:path>')
def static_directory(path):
    return send_from_directory("static", path)


@app.route("/upload", methods=["POST"])
def upload_file():
    for file in request.files.values():
        document_id = str(uuid.uuid4())
        path = save(document_id, file)

        worker.add_path(document_id, file.mimetype, file.filename, path)

    return {"success": True}


@app.route("/add_url", methods=["POST"])
def add_url():
    url = request.json["url"]
    document_id = str(uuid.uuid4())
    worker.add_url(document_id, url)

    return {"success": True}


@app.route("/download/<uuid>", methods=["GET"])
def download_file(uuid):
    document = database.select_document(uuid)

    if document is None:
        return render_template("not_found.html")

    return send_file(
        open(document.path, "rb"),
        mimetype=document.mimetype,
        download_name=document.name,
    )


@app.route("/api/languages", methods=["POST"])
def api_languages():
    return {"success": True, "languages": LANGUAGES}


@app.route("/api/query", methods=["POST"])
def api_query():
    language = request.json["language"]
    query = request.json["query"]
    result = answer_query(database, query, language)

    if result.success:
        return {
            "success": True,
            "result": {
                "query": query,
                "text": result.text,
                "documents": result.documents,
                "images": result.images,
            }
        }
    else:
        return {"success": False}


@app.route("/api/select", methods=["POST"])
def api_select():
    documents = [{
        "uuid": document.uuid,
        "filename": document.name,
        "mimetype": document.mimetype
    } for document in database.select_documents()]

    return {"success": True, "documents": documents}


@app.route("/api/remove", methods=["POST"])
def api_remove():
    uuid = request.json["uuid"]
    database.remove_document(uuid)

    return {"success": True}


if __name__ == "__main__":
    worker.start()
    app.run(debug=True)
