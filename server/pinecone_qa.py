from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone

import os
import pinecone
import shutil
import time


def time_decorator(func):
    def wrapper_function(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Finished {func.__name__!r} in {end - start:.4f} seconds")
        return result

    return wrapper_function


@time_decorator
def init_pinecone(pinecone_api_key, pinecone_environment):
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)


@time_decorator
def load_docs(directory):
    loader = DirectoryLoader(directory)
    documents = loader.load()
    return documents


@time_decorator
def split_docs(documents, chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs_splitted = text_splitter.split_documents(documents)
    return docs_splitted


@time_decorator
def create_query_embeddings(query):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(query)


@time_decorator
def create_document_embeddings(documents):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_documents(documents)


@time_decorator
def purge_pinecone_index(index_name, document_directory_indexed):
    delete_all_files_in_dir(document_directory_indexed)
    create_pinecone_index(index_name, True)


def delete_all_files_in_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@time_decorator
def create_pinecone_index(index_name, force=False):
    indexes = pinecone.list_indexes()
    if index_name in indexes:
        print(f"Pinecone index {index_name} already exists")
        if force:
            print(f"Dropping Pinecone index {index_name}")
            pinecone.delete_index(index_name)
        else:
            print(f"Keep existing Pinecone index {index_name}")
            return
    print(f"Creating Pinecone index {index_name}")
    pinecone.create_index(index_name, dimension=1536, timeout=60)
    print(f"Pinecone index {index_name} successfully created")

@time_decorator
def build_pinecone_index(docs, index_name):
    print(f"Start building Pinecone index {index_name}")
    embeddings = OpenAIEmbeddings()
    index = Pinecone.from_documents(docs, embeddings, index_name=index_name)
    print(f"Done building Pinecone index {index_name}")
    return index


@time_decorator
def get_similiar_docs(index, query, k=2, score=False):
    if score:
        similar_docs = index.similarity_search_with_score(query, k=k)
    else:
        similar_docs = index.similarity_search(query, k=k)
    return similar_docs


@time_decorator
def get_chain():
    model_name = "gpt-3.5-turbo"  # other options: "text-davinci-003", "gpt-4"
    llm = ChatOpenAI(model_name=model_name)
    return load_qa_chain(llm, chain_type="stuff")


@time_decorator
def get_answer(index, query):
    similar_docs = get_similiar_docs(index, query)
    chain = get_chain()
    result = chain.run(input_documents=similar_docs, question=query)
    return result


@time_decorator
def get_answer_with_sources(index, query):
    retriever = index.as_retriever()
    model_name = "gpt-3.5-turbo"  # other options: "text-davinci-003", "gpt-4"
    llm = ChatOpenAI(model_name=model_name)
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    res = qa(query)
    result, source_docs = res["result"], res["source_documents"]
    sources = set()
    for document in source_docs:
        sources.add(document.metadata["source"].split("/")[-1])
    return result, sources


def move_files_to_directory(source_dir, target_dir):
    print(f"Moving files from {source_dir} to {target_dir}")
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        print(f"Moving file {file_name} from {source_dir} to {target_dir}")
        shutil.move(os.path.join(source_dir, file_name), os.path.join(target_dir, file_name))


def build_docs_index(document_directory, index_name, document_directory_indexed):
    raw_docs = load_docs(document_directory)
    splitted_docs = split_docs(raw_docs)
    create_pinecone_index(index_name)
    move_files_to_directory(document_directory, document_directory_indexed)
    return build_pinecone_index(splitted_docs, index_name)


def print_question_answer(question, answer, sources):
    separator = "#" * 80
    print(
        f"{separator}\nQuestion: {question}:\nAnswer: {answer}\nSource: {sources}\n{separator}\n"
    )
