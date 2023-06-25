from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from pinecone_qa import (
    init_pinecone,
    build_docs_index,
    get_answer_with_sources,
    purge_pinecone_index,
)
import os


load_dotenv()
document_directory = os.environ.get("DOCUMENT_DIRECTORY")
document_directory_indexed = os.environ.get("DOCUMENT_DIRECTORY_INDEXED")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT")
pinecone_index = os.environ.get("PINECONE_INDEX")

init_pinecone(pinecone_api_key, pinecone_environment)
docs_index = build_docs_index(
    document_directory,
    pinecone_index,
    document_directory_indexed,
)

app = Flask(__name__)
CORS(app)


@app.route("/purge", methods=["GET"])
def purge_index():
    purge_pinecone_index(pinecone_index, document_directory_indexed)
    return jsonify(response="Success")


@app.route("/ingest", methods=["GET"])
def ingest_data():
    global docs_index
    docs_index = build_docs_index(
        document_directory,
        pinecone_index,
        document_directory_indexed
    )
    return jsonify(response="Success")


@app.route("/get_ingested_files", methods=["GET"])
def get_ingested_files():
    file_names = []
    if os.path.exists(document_directory_indexed):
        file_names = os.listdir(document_directory_indexed)
    return jsonify(ingested_files=file_names)


@app.route("/get_answer", methods=["POST"])
def get_answer():
    global docs_index
    query = request.json
    if query:
        answer, sources = get_answer_with_sources(docs_index, query)
        list_sources = []
        for source in sources:
            list_sources.append({"name": source})
        return jsonify(query=query, answer=answer, source=list_sources)
    return "Empty Query", 400


@app.route("/upload_doc", methods=["POST"])
def upload_doc():
    if "document" not in request.files:
        return jsonify(response="No files found"), 400

    document = request.files["document"]
    if document.filename == "":
        return jsonify(response="No file selected!"), 400

    filename = document.filename
    save_path = os.path.join(document_directory, filename)
    document.save(save_path)

    global docs_index
    docs_index = build_docs_index(
        document_directory,
        pinecone_index,
        document_directory_indexed
    )

    return jsonify(response="Document uploaded successfully")


@app.route("/upload_files", methods=["POST"])
def upload_files():
    print(f"upload_files triggered")
    if "documents" not in request.files:
        return jsonify(response="No files found"), 400

    files = request.files.getlist('documents')
    for file in files:
        print(f"file: {file.filename}")
        if file and file.filename != '':
            file.save(os.path.join(document_directory, file.filename))

    global docs_index
    docs_index = build_docs_index(
        document_directory,
        pinecone_index,
        document_directory_indexed
    )

    return jsonify(response="Files uploaded successfully")


if __name__ == "__main__":
    print("Starting HelpGPT ...")
    app.run(host="0.0.0.0", port=5555, debug=False)
