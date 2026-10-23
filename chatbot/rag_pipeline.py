import os
from dotenv import load_dotenv

load_dotenv()

try:
    from huggingface_hub import hf_hub_download
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    HAS_VECTOR_DB = True
except Exception:
    HAS_VECTOR_DB = False

VECTOR_DB_REPO_ID = "neerajbodinapalli/agri-guide-vector-db"
_vectorstore       = None


def get_vectorstore():
    global _vectorstore
    if not HAS_VECTOR_DB:
        return None

    if _vectorstore is None:
        print("Loading vector database (first request)...")
        embeddings = HuggingFaceEmbeddings(
            model_name    = "all-MiniLM-L6-v2",
            model_kwargs  = {"device": "cpu"},
            encode_kwargs = {"normalize_embeddings": True}
        )

        # Download FAISS index and metadata from Hugging Face Hub
        index_path = hf_hub_download(
            repo_id=VECTOR_DB_REPO_ID,
            filename="index.faiss",
        )
        metadata_path = hf_hub_download(
            repo_id=VECTOR_DB_REPO_ID,
            filename="metadata.json",
        )

        # Load vectorstore from local files
        _vectorstore = FAISS.load_local(
            os.path.dirname(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("Vector database loaded.")
    return _vectorstore


def retrieve_context(query: str, prediction_context: dict = None, k: int = 4) -> tuple[str, list[str]]:
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return "", []

    enriched_query = query

    if prediction_context:
        feature = prediction_context.get("feature", "")

        if feature == "crop_recommendation":
            crop           = prediction_context.get("crop", "")
            enriched_query = f"{crop} crop cultivation soil water requirements {query}"

        elif feature == "yield_prediction":
            crop           = prediction_context.get("crop", "")
            season         = prediction_context.get("season", "")
            enriched_query = f"{crop} {season} yield improvement farming practices {query}"

        elif feature == "soil_health":
            fertilizer     = prediction_context.get("fertilizer", "")
            enriched_query = f"{fertilizer} fertilizer application soil health {query}"

        elif feature == "disease_detection":
            crop           = prediction_context.get("crop", "")
            disease        = prediction_context.get("disease", "")
            enriched_query = f"{crop} {disease} plant foliar fungal disease symptoms treatment fungicide management {query}"

    docs = vectorstore.similarity_search(enriched_query, k=k)

    context_parts = []
    sources       = []

    for doc in docs:
        context_parts.append(doc.page_content)
        source = doc.metadata.get("source", "knowledge base")
        if source not in sources:
            sources.append(source)

    return "\n\n---\n\n".join(context_parts), sources