import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE_DIR = "knowledge_base"
VECTOR_DB_DIR      = "vector_db"


CSV_FILES = {
    "raw_data/Crop_recommendation.csv" : "crop_recommendation",
    "Fertilizer_Prediction.csv"        : "fertilizer_data",
}

CATEGORY_MAP = {
    "organic_farming_guide.pdf"             : "general_farming",
    "plant_disease_management_protocol.pdf" : "disease_treatment",
    "package_of_practices.pdf"             : "crop_cultivation",
}

# ── PDF Loader ─────────────────────────────────────────────────────────────────
def load_pdfs():
    docs    = []
    pdf_dir = Path(KNOWLEDGE_BASE_DIR)
    pdf_files = list(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"WARNING: No PDF files found in '{KNOWLEDGE_BASE_DIR}/'")
        print("         Place your PDFs there and re-run.")
        return docs

    for pdf_file in pdf_files:
        print(f"  Loading PDF: {pdf_file.name}")
        try:
            loader   = PyPDFLoader(str(pdf_file))
            pages    = loader.load()
            category = CATEGORY_MAP.get(pdf_file.name, "general_farming")
            for page in pages:
                page.metadata["source"]   = pdf_file.name
                page.metadata["category"] = category
            docs.extend(pages)
            print(f"    → {len(pages)} pages loaded")
        except Exception as e:
            print(f"    ERROR loading {pdf_file.name}: {e}")

    print(f"  Total PDF pages: {len(docs)}\n")
    return docs

# ── CSV → Sentence Converter ───────────────────────────────────────────────────
def csv_row_to_sentence(row, csv_type: str) -> str:
    if csv_type == "crop_recommendation":
        return (
            f"{row.get('label', 'Unknown crop')} grows well with nitrogen {row.get('N', '?')} kg/ha, "
            f"phosphorus {row.get('P', '?')} kg/ha, potassium {row.get('K', '?')} kg/ha, "
            f"temperature {row.get('temperature', '?')} degrees Celsius, "
            f"humidity {row.get('humidity', '?')}%, pH {row.get('ph', '?')}, "
            f"and rainfall {row.get('rainfall', '?')} mm."
        )
    elif csv_type == "crop_production":
        return (
            f"{row.get('Crop', 'Unknown crop')} is grown in {row.get('State_Name', 'unknown state')} "
            f"during {row.get('Season', 'unknown season')} season. "
            f"Area: {row.get('Area', '?')} hectares, Production: {row.get('Production', '?')} tonnes."
        )
    elif csv_type == "fertilizer_data":
        return (
            f"For {row.get('Crop Type', 'unknown crop')} on {row.get('Soil Type', 'unknown soil')} soil "
            f"with temperature {row.get('Temparature', '?')} degrees, humidity {row.get('Humidity', '?')}%, "
            f"nitrogen {row.get('Nitrogen', '?')}, phosphorus {row.get('Phosphorous', '?')}, "
            f"potassium {row.get('Potassium', '?')}, "
            f"the recommended fertilizer is {row.get('Fertilizer Name', 'unknown')}."
        )
    return str(row.to_dict())


def load_csvs():
    docs = []
    for csv_path, csv_type in CSV_FILES.items():
        if not Path(csv_path).exists():
            print(f"  WARNING: {csv_path} not found — skipping.")
            continue
        print(f"  Loading CSV: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                sentence = csv_row_to_sentence(row, csv_type)
                docs.append(Document(
                    page_content=sentence,
                    metadata={"source": csv_path, "category": "agricultural_data"}
                ))
            print(f"    → {len(df)} rows converted to sentences")
        except Exception as e:
            print(f"    ERROR loading {csv_path}: {e}")

    print(f"  Total CSV documents: {len(docs)}\n")
    return docs

# ── Main Build ─────────────────────────────────────────────────────────────────
def build_vector_db():
    print("=" * 60)
    print("  Agri-Guide — Vector Database Builder")
    print("  Using: Sentence Transformers (fully local, no API)")
    print("=" * 60)

    # 1. Load all documents
    print("\n[1/4] Loading documents...")
    pdf_docs = load_pdfs()
    csv_docs = load_csvs()
    all_docs = pdf_docs + csv_docs

    if not all_docs:
        print("ERROR: No documents loaded. Check your knowledge_base/ folder and CSV paths.")
        return

    print(f"  Total documents loaded: {len(all_docs)}")

    # 2. Split into chunks
    print("\n[2/4] Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size    = 2000,   # larger = fewer chunks = faster processing
        chunk_overlap = 100,
        separators    = ["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(all_docs)
    print(f"  Total chunks: {len(chunks)}")

    # 3. Generate embeddings locally
    print("\n[3/4] Loading Sentence Transformer model...")
    print("  (First run downloads ~90MB model — subsequent runs are instant)")
    embeddings = HuggingFaceEmbeddings(
        model_name    = "all-MiniLM-L6-v2",
        model_kwargs  = {"device": "cpu"},
        encode_kwargs = {"normalize_embeddings": True}
    )

    print("  Generating embeddings locally (no API, no quota)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    print(f"  Done — {len(chunks)} chunks embedded.")

    # 4. Save to disk
    print("\n[4/4] Saving vector database...")
    Path(VECTOR_DB_DIR).mkdir(exist_ok=True)
    vectorstore.save_local(VECTOR_DB_DIR)
    print(f"  Saved to: {VECTOR_DB_DIR}/")

    # Save metadata summary
    metadata_summary = {}
    for chunk in chunks:
        cat = chunk.metadata.get("category", "unknown")
        metadata_summary[cat] = metadata_summary.get(cat, 0) + 1

    with open(f"{VECTOR_DB_DIR}/metadata.json", "w") as f:
        json.dump(metadata_summary, f, indent=2)

    print("\n  Chunk distribution:")
    for cat, count in metadata_summary.items():
        print(f"    {cat}: {count} chunks")

    print("\n" + "=" * 60)
    print("  Done! Vector database is ready.")
    print("  Next step: python chatbot/test_chatbot.py")
    print("=" * 60)


if __name__ == "__main__":
    build_vector_db()