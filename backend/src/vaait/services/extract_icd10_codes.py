import os
import pickle
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever, PreProcessor

doc_dir = "/documents"
filepaths = [doc_dir + "/" + f for f in os.listdir(doc_dir)]

def remove_html_tags_and_add_filename(filepath: str) -> dict[str, Any]:
    file_path = Path(filepath)
    filename = file_path.stem
    with file_path.open("rb") as f:
        content = pickle.load(f)  # noqa: S301
    cleaned_text = BeautifulSoup(content.decode("utf-8"), "html.parser").get_text(separator="")
    return {"content": cleaned_text.replace("\n", " ").replace("\r", ""), "meta": {"name": filename}}

preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=False,
    split_by="word",
    split_length=300,
    split_respect_sentence_boundary=True,
    )

preprocessed_docs = preprocessor.process([remove_html_tags_and_add_filename(f) for f in filepaths])

try:
    document_store = FAISSDocumentStore(embedding_dim=384)
    document_store.write_documents(preprocessed_docs)
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/all-MiniLM-L12-v2", use_gpu=True,
    )
    document_store.update_embeddings(retriever)
    document_store.save("my_document_store.faiss")
except ValueError:
    document_store = FAISSDocumentStore.load("my_document_store.faiss")
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/all-MiniLM-L12-v2", use_gpu=True,
    )

def retrieve_icd10_code(entity: str) -> str:
    result = retriever.retrieve(entity, top_k=1)[0]
    return result.meta["name"].split("_")[-1]
