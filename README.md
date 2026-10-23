# 🌱 CropPulse: Intelligent Precision Farming Suite (ML + CV + RAG Chatbot)

CropPulse is an advanced precision agriculture intelligence platform that combines **classical Machine Learning**, **Computer Vision foliar disease diagnosis**, and an integrated **RAG (Retrieval-Augmented Generation) agricultural assistant** to empower farmers with data-driven decision-making across crop planning, yield forecasting, soil nutrition, and crop pathology.

## 🌟 Core Features

- 🌾 **Crop Recommendation (ML)**: Suggests optimal crops based on NPK soil chemistry, climate temperature, humidity, and rainfall.
- 📈 **Yield Prediction (ML)**: Predicts expected yield per hectare and total production across 124 Indian agricultural crops and 28 states/UTs.
- 🧪 **Soil Health & Fertilizer Advisor (ML)**: Analyzes NPK balances and soil moisture to recommend precise fertilizer types and soil conditioning guidelines.
- 🔬 **Plant Disease Scanner (ML + Computer Vision)**: Fast classical CV foliar biomarker analysis (color moments, HSV distributions, Laplacian texture energy, chlorosis/necrosis ratios) detecting 15 crop disease conditions with organic & chemical treatment remedies.
- 💬 **CropPulse Assistant (RAG Chatbot)**:
  - Interactive embedded assistant across all suite pages.
  - Context-aware retrieval over agricultural knowledge base documents.

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Flask, Jinja2 WSGI
- **Machine Learning & CV**: scikit-learn (RandomForest, ExtraTrees, SVC), SciPy, NumPy, Pillow
- **Deployment**: Vercel Serverless (`@vercel/python`, `vercel.json`, `api/index.py`), Render, Gunicorn


##  Updated Project Structure 

```
.
├── web_app.py                      # Flask app: UI routes + ML/RAG APIs
├── app.py                          # Training entry point (runs training pipeline)
├── requirements.txt
├── startup.sh                      # Deploy: trains models if missing, then starts Gunicorn
├── render.yaml                     # Render deployment config
├── Procfile                        # Procfile for platforms using it
│
├── agri_guide/                     # Training pipeline package
│   ├── components/                 # Data ingestion/transformation + trainers
│   └── pipeline/training_pipeline.py
│
├── templates/                      # UI templates
│   ├── home.html
│   ├── crop_recommendation.html
│   ├── yield_prediction.html
│   └── soil_health.html
│
├── static/
│   ├── css/style.css
│   └── js/
│       ├── chatbot.js              # Chat widget frontend
│       ├── crop_recommendation.js
│       ├── yield_prediction.js
│       ├── soil_health.js
│       └── main.js
│
├── final_model/                    # Trained ML artifacts (created by training)
│   ├── crop_recommendation_model.pkl
│   ├── label_encoder.pkl
│   ├── yield_model.pkl
│   ├── yield_scaler.pkl
│   ├── yield_feature_columns.pkl
│   ├── yield_state_encoder.pkl
│   ├── yield_season_encoder.pkl
│   ├── yield_crop_encoder.pkl
│   ├── fertilizer_model.pkl
│   ├── soil_encoder.pkl
│   ├── crop_encoder.pkl
│   └── fertilizer_encoder.pkl
│
├── chatbot/
│   ├── chat_service.py             # OpenRouter chat + history + guardrails
│   ├── rag_pipeline.py             # FAISS retrieval (loads on first request)
│   ├── build_vector_db.py          # Build vector_db/ from PDFs + CSVs
│   └── prompt_template.py
│
├── knowledge_base/
│   ├── organic_farming_guide.pdf
│   └── package_of_practices.pdf
│
├── vector_db/                      # FAISS index + metadata (used by RAG)
│   └── metadata.json
│
└── raw_data/
    ├── Crop_recommendation.csv
    └── crop_production.csv
```
```

##  Installation (Local)

### Prerequisites

- Python **3.9+** recommended (Render config uses 3.9.16)

### Setup

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

##  Environment Variables

Create a `.env` file in the project root (or set env vars in your OS/deployment):

```env
# Required for the chatbot (OpenRouter)
OPENROUTER_API_KEY=your_key_here

# Optional (only used by chatbot/check_models.py)
GOOGLE_API_KEY=your_key_here
```

##  Required Assets (Important)

- **ML model `.pkl` files**:
  - Either **train locally** via `python app.py`, or let deployment auto-download / auto-train using `startup.sh`

## 🚀 Run the Application

### Option A: Run the Web App (recommended)

```bash
python web_app.py
```

Open:
- **Home**: `http://localhost:5000/`
- **Crop Recommendation**: `http://localhost:5000/crop-recommendation`
- **Yield Prediction**: `http://localhost:5000/yield-prediction`
- **Soil Health**: `http://localhost:5000/soil-health`

### Option B: Train / Retrain ML Models

```bash
python app.py
```

This runs the training pipeline (`agri_guide/pipeline/training_pipeline.py`) and writes artifacts into `final_model/`.

##  RAG Chatbot (Vector DB)

The chatbot retrieves answers from a local FAISS vector database in `vector_db/`.

### Build / Rebuild the Vector DB

```bash
python chatbot/build_vector_db.py
```

Sources used:
- PDFs in `knowledge_base/`
- CSVs: `raw_data/Crop_recommendation.csv`, `Fertilizer_Prediction.csv` (as configured in `chatbot/build_vector_db.py`)

##  API Endpoints (Backend)

- **Health**: `GET /api/health`
- **Crop prediction**: `POST /api/predict-crop`
- **Yield prediction**: `POST /api/predict-yield`
- **Fertilizer prediction**: `POST /api/predict-fertilizer`
- **Chatbot**: `POST /api/chat` (JSON: `message`, `session_id`, optional `context`)

##  System Flowchart (End-to-End)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                  DATA / ASSETS                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ ML Datasets: raw_data/Crop_recommendation.csv, raw_data/crop_production.csv  │
│            Fertilizer_Prediction.csv                                         │
│ RAG Docs:   knowledge_base/*.pdf  (+ CSV sentences during build)             │
└──────────────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────────────────────┐
        │                           (1) ML                              │
        └──────────────────────────────────────────────────────────────┘
┌───────────────────────────────┐                ┌──────────────────────────────┐
│ app.py                         │                │ final_model/                  │
│ agri_guide training pipeline    │ ───────────▶   │ *.pkl models + encoders       │
│ - crop recommendation           │                │ (crop, yield, fertilizer)     │
│ - yield prediction              │                └──────────────────────────────┘
│ - fertilizer prediction         │
└───────────────────────────────┘

        ┌──────────────────────────────────────────────────────────────┐
        │                           (2) RAG                             │
        └──────────────────────────────────────────────────────────────┘
┌───────────────────────────────┐                ┌──────────────────────────────┐
│ chatbot/build_vector_db.py     │                │ vector_db/ (FAISS index)      │
│ PDFs + CSV sentences → chunks  │ ───────────▶   │ loaded on first chat request  │
│ embeddings (MiniLM) → FAISS    │                └──────────────────────────────┘
└───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           Flask Web App (web_app.py)                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ UI: /, /crop-recommendation, /yield-prediction, /soil-health                 │
│ APIs: /api/predict-crop, /api/predict-yield, /api/predict-fertilizer,        │
│      /api/chat                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────┐                ┌──────────────────────────────┐
│ Frontend forms + results       │                │ Chat widget (static/js/chatbot.js)│
│ templates/ + static/js         │                │ /api/chat + optional context  │
└───────────────────────────────┘                └──────────────────────────────┘
```
```



