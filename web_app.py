"""
CropPulse Web Application
A modern Flask-based web interface for precision farming and yield optimization.
"""

import pickle
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv()

import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from huggingface_hub import hf_hub_download

from chatbot.chat_service import chat as chatbot_chat
from crop_manager import CropManager
from agri_guide.utils.disease_detector import predict_disease

HF_REPO_ID = "neerajbodinapalli/agri-guide-models"

app = Flask(__name__)
app.config["SECRET_KEY"] = "agri-guide-secret-key-2024"

@app.context_processor
def inject_supabase_credentials():
    return {
        'supabase_url': os.environ.get('SUPABASE_URL', ''),
        'supabase_anon_key': os.environ.get('SUPABASE_ANON_KEY', '')
    }

# Load models and preprocessors at startup
MODEL_DIR = Path(__file__).parent

# Crop Recommendation Models
CROP_MODEL_PATH = MODEL_DIR / "final_model" / "crop_recommendation_model.pkl"
CROP_SCALER_PATH = MODEL_DIR / "final_model" / "scaler.pkl"
CROP_LABEL_ENCODER_PATH = MODEL_DIR / "final_model" / "label_encoder.pkl"

# Yield Prediction Models
YIELD_MODEL_PATH = MODEL_DIR / "final_model" / "yield_model.pkl"
YIELD_SCALER_PATH = MODEL_DIR / "final_model" / "yield_scaler.pkl"
YIELD_FEATURE_COLUMNS_PATH = MODEL_DIR / "final_model" / "yield_feature_columns.pkl"
YIELD_STATE_ENCODER_PATH = MODEL_DIR / "final_model" / "yield_state_encoder.pkl"
YIELD_SEASON_ENCODER_PATH = MODEL_DIR / "final_model" / "yield_season_encoder.pkl"
YIELD_CROP_ENCODER_PATH = MODEL_DIR / "final_model" / "yield_crop_encoder.pkl"

# Fertilizer Prediction Models
FERTILIZER_MODEL_PATH = MODEL_DIR / "final_model" / "fertilizer_model.pkl"
SOIL_ENCODER_PATH = MODEL_DIR / "final_model" / "soil_encoder.pkl"
CROP_ENCODER_PATH = MODEL_DIR / "final_model" / "crop_encoder.pkl"
FERTILIZER_ENCODER_PATH = MODEL_DIR / "final_model" / "fertilizer_encoder.pkl"

# Raw data path for populating dropdowns
RAW_DATA_DIR = MODEL_DIR / "raw_data"
YIELD_DATA_PATH = RAW_DATA_DIR / "crop_production.csv"

# Filenames of models and preprocessors stored on Hugging Face Hub
# (paths are relative to the root of the HF model repo)
CROP_MODEL_FILENAME = "final_model/crop_recommendation_model.pkl"
CROP_SCALER_FILENAME = "final_model/scaler.pkl"
CROP_LABEL_ENCODER_FILENAME = "final_model/label_encoder.pkl"

YIELD_MODEL_FILENAME = "final_model/yield_model.pkl"
YIELD_SCALER_FILENAME = "final_model/yield_scaler.pkl"
YIELD_FEATURE_COLUMNS_FILENAME = "final_model/yield_feature_columns.pkl"
YIELD_STATE_ENCODER_FILENAME = "final_model/yield_state_encoder.pkl"
YIELD_SEASON_ENCODER_FILENAME = "final_model/yield_season_encoder.pkl"
YIELD_CROP_ENCODER_FILENAME = "final_model/yield_crop_encoder.pkl"

FERTILIZER_MODEL_FILENAME = "final_model/fertilizer_model.pkl"
SOIL_ENCODER_FILENAME = "final_model/soil_encoder.pkl"
CROP_ENCODER_FILENAME = "final_model/crop_encoder.pkl"
FERTILIZER_ENCODER_FILENAME = "final_model/fertilizer_encoder.pkl"

# Global model variables
crop_model = None
crop_scaler = None
crop_label_encoder = None
yield_model = None
yield_scaler = None
yield_feature_columns = None
yield_state_encoder = None
yield_season_encoder = None
yield_crop_encoder = None

# Fertilizer prediction models
fertilizer_model = None
soil_encoder = None
crop_encoder = None
fertilizer_encoder = None

# Global metadata for yield dropdowns
yield_states: list[str] | None = None
yield_seasons: list[str] | None = None
yield_crops: list[str] | None = None

def get_artifact_path(local_path: Path, hf_filename: str) -> Path:
    """Return local path if file exists, otherwise download from Hugging Face Hub."""
    if local_path.exists():
        return local_path
    return Path(hf_hub_download(repo_id=HF_REPO_ID, filename=hf_filename))


def load_models():
    """Load all ML models and preprocessors from local storage or Hugging Face Hub."""
    global crop_model, crop_scaler, crop_label_encoder
    global yield_model, yield_scaler, yield_feature_columns
    global yield_state_encoder, yield_season_encoder, yield_crop_encoder
    global fertilizer_model, soil_encoder, crop_encoder, fertilizer_encoder
    
    try:
        # Load from local final_model directory if present, otherwise download from HF Hub
        crop_model_path = get_artifact_path(CROP_MODEL_PATH, CROP_MODEL_FILENAME)
        crop_scaler_path = get_artifact_path(CROP_SCALER_PATH, CROP_SCALER_FILENAME)
        crop_label_encoder_path = get_artifact_path(CROP_LABEL_ENCODER_PATH, CROP_LABEL_ENCODER_FILENAME)

        yield_model_path = get_artifact_path(YIELD_MODEL_PATH, YIELD_MODEL_FILENAME)
        yield_scaler_path = get_artifact_path(YIELD_SCALER_PATH, YIELD_SCALER_FILENAME)
        yield_feature_columns_path = get_artifact_path(YIELD_FEATURE_COLUMNS_PATH, YIELD_FEATURE_COLUMNS_FILENAME)
        yield_state_encoder_path = get_artifact_path(YIELD_STATE_ENCODER_PATH, YIELD_STATE_ENCODER_FILENAME)
        yield_season_encoder_path = get_artifact_path(YIELD_SEASON_ENCODER_PATH, YIELD_SEASON_ENCODER_FILENAME)
        yield_crop_encoder_path = get_artifact_path(YIELD_CROP_ENCODER_PATH, YIELD_CROP_ENCODER_FILENAME)

        fertilizer_model_path = get_artifact_path(FERTILIZER_MODEL_PATH, FERTILIZER_MODEL_FILENAME)
        soil_encoder_path = get_artifact_path(SOIL_ENCODER_PATH, SOIL_ENCODER_FILENAME)
        crop_encoder_path = get_artifact_path(CROP_ENCODER_PATH, CROP_ENCODER_FILENAME)
        fertilizer_encoder_path = get_artifact_path(FERTILIZER_ENCODER_PATH, FERTILIZER_ENCODER_FILENAME)

        # Load crop recommendation models
        with open(crop_model_path, 'rb') as f:
            crop_model = pickle.load(f)
        with open(crop_scaler_path, 'rb') as f:
            crop_scaler = pickle.load(f)
        with open(crop_label_encoder_path, 'rb') as f:
            crop_label_encoder = pickle.load(f)

        # Load yield prediction models
        with open(yield_model_path, 'rb') as f:
            yield_model = pickle.load(f)
        with open(yield_scaler_path, 'rb') as f:
            yield_scaler = pickle.load(f)
        with open(yield_feature_columns_path, 'rb') as f:
            yield_feature_columns = pickle.load(f)

        # Load label encoders for yield prediction
        with open(yield_state_encoder_path, 'rb') as f:
            yield_state_encoder = pickle.load(f)
        with open(yield_season_encoder_path, 'rb') as f:
            yield_season_encoder = pickle.load(f)
        with open(yield_crop_encoder_path, 'rb') as f:
            yield_crop_encoder = pickle.load(f)

        # Load fertilizer prediction models
        with open(fertilizer_model_path, 'rb') as f:
            fertilizer_model = pickle.load(f)
        with open(soil_encoder_path, 'rb') as f:
            soil_encoder = pickle.load(f)
        with open(crop_encoder_path, 'rb') as f:
            crop_encoder = pickle.load(f)
        with open(fertilizer_encoder_path, 'rb') as f:
            fertilizer_encoder = pickle.load(f)

        print("All models loaded successfully from Hugging Face Hub!")
        print(f"[OK] Crop model loaded: {crop_model is not None}")
        print(f"[OK] Yield model loaded: {yield_model is not None}")
        print(f"[OK] Fertilizer model loaded: {fertilizer_model is not None}")
    except Exception as e:
        print(f"[ERROR] Error loading models from Hub: {e}")
        import traceback
        traceback.print_exc()
        raise


def load_yield_metadata() -> None:
    """Load unique states, seasons, and crops for the yield prediction form."""
    global yield_states, yield_seasons, yield_crops

    # Only load once
    if yield_states is not None and yield_seasons is not None and yield_crops is not None:
        return

    try:
        data_path = YIELD_DATA_PATH if YIELD_DATA_PATH.exists() else (MODEL_DIR / "crop_production.csv")
        if data_path.exists():
            df = pd.read_csv(data_path)
            yield_states = sorted(df["State_Name"].dropna().unique().tolist())
            yield_seasons = sorted(df["Season"].dropna().unique().tolist())
            yield_crops = sorted(df["Crop"].dropna().unique().tolist())
            return
    except Exception as exc:
        print(f"Error loading yield metadata from file: {exc}")

    # Fallback to encoders if CSV file is not present
    try:
        if yield_state_encoder is not None:
            yield_states = sorted([str(s).strip() for s in yield_state_encoder.classes_])
        else:
            yield_states = []

        if yield_season_encoder is not None:
            yield_seasons = sorted(list({str(s).strip() for s in yield_season_encoder.classes_}))
        else:
            yield_seasons = []

        if yield_crop_encoder is not None:
            yield_crops = sorted([str(c).strip() for c in yield_crop_encoder.classes_])
        else:
            yield_crops = []
    except Exception as exc:
        print(f"Error loading yield metadata from encoders: {exc}")
        yield_states, yield_seasons, yield_crops = [], [], []


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features for crop recommendation."""
    df_fe = df.copy()
    df_fe["NPK_sum"] = df_fe["N"] + df_fe["P"] + df_fe["K"]
    df_fe["N_K_ratio"] = df_fe["N"] / (df_fe["K"] + 1e-3)
    df_fe["temp_humidity_index"] = df_fe["temperature"] * df_fe["humidity"] / 100.0
    df_fe["is_acidic"] = (df_fe["ph"] < 7).astype(int)
    df_fe["rainfall_per_NPK"] = df_fe["rainfall"] / (df_fe["NPK_sum"] + 1e-3)
    return df_fe


def parse_numeric(
    val: Any,
    field_name: str,
    min_val: float | None = None,
    max_val: float | None = None,
    default: float | None = None,
) -> float:
    """Safely parse and validate a numeric field from request JSON."""
    if val is None or (isinstance(val, str) and val.strip() == ""):
        if default is not None:
            return float(default)
        raise ValueError(f"Field '{field_name}' is required")

    try:
        num = float(val)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{field_name}' must be a valid number, got {repr(val)}")

    if np.isnan(num) or np.isinf(num):
        raise ValueError(f"Field '{field_name}' must be a finite number")

    min_disp = (int(min_val) if float(min_val).is_integer() else min_val) if min_val is not None else None
    max_disp = (int(max_val) if float(max_val).is_integer() else max_val) if max_val is not None else None

    if min_val is not None and num < min_val:
        range_str = f" ({field_name} must be between {min_disp} and {max_disp})" if max_val is not None else ""
        raise ValueError(f"Field '{field_name}' must be >= {min_val}{range_str}")

    if max_val is not None and num > max_val:
        range_str = f" ({field_name} must be between {min_disp} and {max_disp})" if min_val is not None else ""
        raise ValueError(f"Field '{field_name}' must be <= {max_val}{range_str}")

    return num


def predict_crop(n, p, k, temperature, humidity, ph, rainfall):
    """Predict the best crop based on soil and climate parameters."""
    if crop_model is None or crop_label_encoder is None:
        raise RuntimeError("Crop recommendation model is not loaded")

    # Safety check for non-finite values
    for val, name in [
        (n, "Nitrogen"), (p, "Phosphorus"), (k, "Potassium"),
        (temperature, "Temperature"), (humidity, "Humidity"),
        (ph, "pH"), (rainfall, "Rainfall")
    ]:
        if np.isnan(val) or np.isinf(val):
            raise ValueError(f"Invalid input: {name} must be a finite number")

    try:
        # Create input DataFrame with columns in the exact order used during training
        # Original columns: N, P, K, temperature, humidity, ph, rainfall
        input_data = pd.DataFrame({
            'N': [float(n)],
            'P': [float(p)],
            'K': [float(k)],
            'temperature': [float(temperature)],
            'humidity': [float(humidity)],
            'ph': [float(ph)],
            'rainfall': [float(rainfall)]
        })
        
        # Add engineered features (this adds: NPK_sum, N_K_ratio, temp_humidity_index, is_acidic, rainfall_per_NPK)
        input_data_fe = add_engineered_features(input_data)
        
        # Ensure columns are in the correct order: original + engineered features
        # The order should match what was used during training (12 features total)
        feature_order = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
                        'NPK_sum', 'N_K_ratio', 'temp_humidity_index', 'is_acidic', 'rainfall_per_NPK']
        
        # Reorder columns to match training order
        input_data_fe = input_data_fe[feature_order]
        
        # Convert to numpy array
        input_array = input_data_fe.values
        
        # Predict (RandomForest model was trained on X_train_fe which is UNSCALED)
        # The model expects 12 features: 7 original + 5 engineered (unscaled)
        prediction_encoded = crop_model.predict(input_array)[0]
        crop_name = crop_label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get prediction probabilities for confidence score
        probabilities = crop_model.predict_proba(input_array)[0]
        confidence = float(np.max(probabilities) * 100)
        
        # Compute secondary alternatives (top runner-up classes)
        top_indices = np.argsort(probabilities)[::-1]
        alternatives = []
        for idx in top_indices[1:4]:
            alt_crop = crop_label_encoder.inverse_transform([idx])[0]
            alt_conf = float(probabilities[idx] * 100)
            if alt_conf >= 0.1:
                alternatives.append({
                    'crop': alt_crop,
                    'confidence': round(alt_conf, 2)
                })

        # Get soil health advice
        advice = generate_soil_advice(float(n), float(p), float(k), float(ph))
        
        return {
            'crop': crop_name,
            'confidence': round(confidence, 2),
            'alternatives': alternatives,
            'advice': advice
        }
    except Exception as e:
        raise Exception(f"Prediction error: {str(e)}")


def generate_soil_advice(n, p, k, ph):
    """Generate fertilizer and soil health advice based on NPK and pH levels."""
    advice_parts = []
    
    # Nitrogen advice
    if n < 50:
        advice_parts.append("N levels are low. Add Urea or Ammonium Nitrate.")
    elif n > 100:
        advice_parts.append("N levels are high. Reduce nitrogen fertilizers.")
    else:
        advice_parts.append("N levels are optimal.")
    
    # Phosphorus advice
    if p < 30:
        advice_parts.append("P levels are low. Add Superphosphate or DAP.")
    elif p > 60:
        advice_parts.append("P levels are high. Reduce phosphorus fertilizers.")
    else:
        advice_parts.append("P levels are optimal.")
    
    # Potassium advice
    if k < 30:
        advice_parts.append("K levels are low. Add Potash or Muriate of Potash.")
    elif k > 80:
        advice_parts.append("K levels are high. Reduce potassium fertilizers.")
    else:
        advice_parts.append("K levels are optimal.")
    
    # pH advice
    if ph < 6.0:
        advice_parts.append("Soil is acidic. Consider adding lime to raise pH.")
    elif ph > 8.0:
        advice_parts.append("Soil is alkaline. Consider adding sulfur or organic matter to lower pH.")
    else:
        advice_parts.append("Soil pH is optimal for most crops.")
    
    return " ".join(advice_parts)


def predict_fertilizer(temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous):
    """Predict the best fertilizer based on soil and crop parameters."""
    if fertilizer_model is None or fertilizer_encoder is None or soil_encoder is None or crop_encoder is None:
        raise RuntimeError("Fertilizer prediction models are not loaded")

    try:
        mapped_crop = CropManager.resolve_for_fertilizer(crop_type)

        # Scale inputs if they come from Crop Recommendation or field tests (kg/ha scale: N up to 140, P up to 145, K up to 200)
        # Training dataset Fertilizer_Prediction.csv has ranges: N in [4, 42], P in [0, 42], K in [0, 19]
        n_in = float(nitrogen)
        p_in = float(phosphorous)
        k_in = float(potassium)

        if n_in > 42.0:
            n_in = min(42.0, (n_in / 140.0) * 42.0)
        if p_in > 42.0:
            p_in = min(42.0, (p_in / 145.0) * 42.0)
        if k_in > 19.0:
            k_in = min(19.0, (k_in / 200.0) * 19.0)

        # Encode categorical variables safely
        try:
            soil_encoded = soil_encoder.transform([str(soil_type).strip()])[0]
        except Exception:
            soil_clean = str(soil_type).strip().lower()
            soil_match = [s for s in soil_encoder.classes_ if str(s).strip().lower() == soil_clean]
            soil_encoded = soil_encoder.transform(soil_match)[0] if soil_match else 0

        try:
            crop_encoded = crop_encoder.transform([mapped_crop])[0]
        except Exception:
            crop_clean = str(mapped_crop).strip().lower()
            crop_match = [c for c in crop_encoder.classes_ if str(c).strip().lower() == crop_clean]
            if crop_match:
                crop_encoded = crop_encoder.transform(crop_match)[0]
            else:
                crop_orig = str(crop_type).strip().lower()
                crop_match2 = [c for c in crop_encoder.classes_ if str(c).strip().lower() == crop_orig]
                crop_encoded = crop_encoder.transform(crop_match2)[0] if crop_match2 else 0

        # Create input DataFrame
        input_data = pd.DataFrame({
            'Temparature': [float(temperature)],  # Note: keeping original column name with typo
            'Humidity ': [float(humidity)],       # Note: keeping original column name with space
            'Moisture': [float(moisture)],
            'Soil Type': [soil_encoded],
            'Crop Type': [crop_encoded],
            'Nitrogen': [n_in],
            'Potassium': [k_in],
            'Phosphorous': [p_in]
        })
        
        # Clean column names (remove extra spaces)
        input_data.columns = input_data.columns.str.strip()
        
        # Convert to numpy array
        input_array = input_data.values
        
        # Predict
        prediction_encoded = fertilizer_model.predict(input_array)[0]
        fertilizer_name = fertilizer_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get prediction probabilities for confidence score
        probabilities = fertilizer_model.predict_proba(input_array)[0]
        confidence = float(np.max(probabilities) * 100)
        
        # Generate soil advice using existing function
        soil_advice = generate_soil_advice(float(nitrogen), float(phosphorous), float(potassium), 7.0)
        
        return {
            'fertilizer': fertilizer_name,
            'confidence': round(confidence, 2),
            'soil_advice': soil_advice
        }
    except Exception as e:
        raise Exception(f"Fertilizer prediction error: {str(e)}")


def predict_yield(state, district, season, crop, area):
    """Predict crop yield based on location, season, crop type, and area."""
    if yield_model is None or yield_scaler is None:
        raise RuntimeError("Yield prediction models are not loaded")

    try:
        mapped_crop = CropManager.resolve_for_yield(crop)

        # Check if the input values are in the encoders' vocabulary
        try:
            state_encoded = yield_state_encoder.transform([str(state).strip()])[0]
        except (ValueError, KeyError):
            state_clean = str(state).strip().lower()
            state_match = [s for s in yield_state_encoder.classes_ if str(s).strip().lower() == state_clean]
            state_encoded = yield_state_encoder.transform(state_match)[0] if state_match else 0
            
        try:
            season_encoded = yield_season_encoder.transform([str(season).strip()])[0]
        except (ValueError, KeyError):
            season_clean = str(season).strip().lower()
            season_match = [s for s in yield_season_encoder.classes_ if str(s).strip().lower() == season_clean]
            season_encoded = yield_season_encoder.transform(season_match)[0] if season_match else 0
            
        try:
            crop_encoded = yield_crop_encoder.transform([mapped_crop])[0]
        except (ValueError, KeyError):
            crop_clean = str(mapped_crop).strip().lower()
            crop_match = [c for c in yield_crop_encoder.classes_ if str(c).strip().lower() == crop_clean]
            if crop_match:
                crop_encoded = yield_crop_encoder.transform(crop_match)[0]
            else:
                crop_orig = str(crop).strip().lower()
                crop_match2 = [c for c in yield_crop_encoder.classes_ if str(c).strip().lower() == crop_orig]
                crop_encoded = yield_crop_encoder.transform(crop_match2)[0] if crop_match2 else 0
        
        area_float = float(area)
        # Create input array with label encoded features
        input_features = np.array([[state_encoded, season_encoded, crop_encoded, area_float]])
        
        # Scale Area feature (it's the last column)
        area_df = pd.DataFrame([[area_float]], columns=getattr(yield_scaler, "feature_names_in_", ["Area"]))
        area_scaled = yield_scaler.transform(area_df)
        input_features[0, 3] = area_scaled[0, 0]  # Replace area with scaled value
        
        # Predict
        yield_prediction = yield_model.predict(input_features)[0]
        yield_per_hectare = round(float(yield_prediction), 2)
        if yield_per_hectare <= 0:
            yield_per_hectare = 0.01
        total_yield = round(yield_per_hectare * area_float, 2)
        if total_yield <= 0:
            total_yield = 0.01
        
        return {
            'yield_per_hectare': yield_per_hectare,
            'total_yield': total_yield,
            'area': area_float
        }
    except Exception as e:
        raise Exception(f"Yield prediction error: {str(e)}")
    except Exception as e:
        raise Exception(f"Yield prediction error: {str(e)}")


# Routes
@app.route('/')
def home():
    """Landing page."""
    return render_template('home.html')


@app.route('/crop-recommendation')
def crop_recommendation():
    """Crop recommendation page."""
    return render_template('crop_recommendation.html')


@app.route("/yield-prediction")
def yield_prediction():
    """Yield prediction page."""
    # Ensure dropdown metadata is loaded
    load_yield_metadata()

    # Optional crop value from query string (used when coming from crop recommendation)
    preselected_crop = request.args.get("crop", "").strip()
    mapped_crop = CropManager.resolve_for_yield(preselected_crop) if preselected_crop else ""
    yield_options = CropManager.get_yield_dropdown_options(yield_crops or [])

    return render_template(
        "yield_prediction.html",
        states=yield_states or [],
        seasons=yield_seasons or [],
        crops=yield_crops or [],
        yield_options=yield_options,
        preselected_crop=preselected_crop,
        mapped_crop=mapped_crop,
    )


@app.route('/soil-health')
def soil_health():
    """Soil health and fertilizer recommendation page."""
    preselected_crop = request.args.get("crop", "").strip()
    mapped_crop = CropManager.resolve_for_fertilizer(preselected_crop) if preselected_crop else ""
    fertilizer_options = CropManager.get_fertilizer_dropdown_options()

    return render_template(
        'soil_health.html',
        preselected_crop=preselected_crop,
        mapped_crop=mapped_crop,
        fertilizer_options=fertilizer_options,
    )


@app.route('/disease-detection')
def disease_detection():
    """Plant disease scanner & leaf diagnostics page."""
    return render_template('disease_detection.html')


@app.route('/api/crop-taxonomy')
def api_crop_taxonomy():
    """Return unified crop taxonomy across the 3 ML models."""
    return jsonify({
        'success': True,
        'data': CropManager.get_unified_crop_metadata()
    })


@app.route('/api/health')
def api_health():
    """Health check endpoint to verify model status."""
    try:
        model_status = {
            'crop_model_loaded': crop_model is not None,
            'yield_model_loaded': yield_model is not None,
            'fertilizer_model_loaded': fertilizer_model is not None,
            'disease_model_loaded': (MODEL_DIR / "final_model" / "disease_model.pkl").exists(),
            'crop_scaler_loaded': crop_scaler is not None,
            'yield_encoders_loaded': all([
                yield_state_encoder is not None,
                yield_season_encoder is not None,
                yield_crop_encoder is not None
            ])
        }
        
        all_loaded = all(model_status.values())
        
        return jsonify({
            'success': True,
            'all_models_loaded': all_loaded,
            'model_status': model_status,
            'message': 'All models loaded successfully' if all_loaded else 'Some models missing'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/predict-crop', methods=['POST'])
def api_predict_crop():
    """API endpoint for crop prediction."""
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'Invalid or missing JSON payload (Bad Request)'}), 400
        if len(data) == 0:
            return jsonify({'success': False, 'error': 'No JSON data provided (Bad Request)'}), 400
            
        # Check if models are loaded
        if crop_model is None or crop_label_encoder is None:
            return jsonify({'success': False, 'error': 'Crop model not loaded'}), 500

        n = parse_numeric(data.get('n'), 'Nitrogen (N)', min_val=0.0, max_val=300.0)
        p = parse_numeric(data.get('p'), 'Phosphorus (P)', min_val=0.0, max_val=300.0)
        k = parse_numeric(data.get('k'), 'Potassium (K)', min_val=0.0, max_val=300.0, default=40.0)
        temperature = parse_numeric(data.get('temperature'), 'Temperature', min_val=-20.0, max_val=65.0, default=25.0)
        humidity = parse_numeric(data.get('humidity'), 'Humidity', min_val=0.0, max_val=100.0, default=70.0)
        ph = parse_numeric(data.get('ph'), 'pH', min_val=0.0, max_val=14.0, default=7.0)
        rainfall = parse_numeric(data.get('rainfall'), 'Rainfall', min_val=0.0, max_val=2000.0, default=100.0)
        
        result = predict_crop(n, p, k, temperature, humidity, ph, rainfall)
        return jsonify({'success': True, 'result': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predict-yield', methods=['POST'])
def api_predict_yield():
    """API endpoint for yield prediction."""
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'Invalid or missing JSON payload'}), 400
            
        # Check if models are loaded
        if yield_model is None or yield_scaler is None:
            return jsonify({'success': False, 'error': 'Yield model not loaded'}), 500

        state = str(data.get('state') or '').strip()
        district = str(data.get('district') or '').strip()  # Not used in model but kept for API compatibility
        season = str(data.get('season') or '').strip()
        crop = str(data.get('crop') or '').strip()
        
        # Validate required fields
        if not state:
            return jsonify({'success': False, 'error': 'State is required'}), 400
        if not season:
            return jsonify({'success': False, 'error': 'Season is required'}), 400
        if not crop:
            return jsonify({'success': False, 'error': 'Crop is required'}), 400

        area = parse_numeric(data.get('area'), 'Area', min_val=0.0001, max_val=10_000_000.0)
        
        result = predict_yield(state, district, season, crop, area)
        return jsonify({'success': True, 'result': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predict-fertilizer', methods=['POST'])
def api_predict_fertilizer():
    """API endpoint for fertilizer prediction."""
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'Invalid or missing JSON payload'}), 400

        # Check if models are loaded
        if fertilizer_model is None or fertilizer_encoder is None:
            return jsonify({'success': False, 'error': 'Fertilizer model not loaded'}), 500

        soil_type = str(data.get('soilType') or data.get('soil_type') or '').strip()
        crop_type = str(data.get('cropType') or data.get('crop_type') or '').strip()
        
        # Validate required fields
        if not soil_type or not crop_type:
            return jsonify({'success': False, 'error': 'Soil Type and Crop Type are required'}), 400

        temperature = parse_numeric(data.get('temperature'), 'Temperature', min_val=-20.0, max_val=65.0)
        humidity = parse_numeric(data.get('humidity'), 'Humidity', min_val=0.0, max_val=100.0)
        moisture = parse_numeric(data.get('moisture'), 'Moisture', min_val=0.0, max_val=100.0)
        nitrogen = parse_numeric(data.get('nitrogen'), 'Nitrogen', min_val=0.0, max_val=500.0)
        potassium = parse_numeric(data.get('potassium'), 'Potassium', min_val=0.0, max_val=500.0)
        p_val = data.get('phosphorous') if data.get('phosphorous') is not None else data.get('phosphorus')
        phosphorous = parse_numeric(p_val, 'Phosphorous', min_val=0.0, max_val=500.0)
        
        result = predict_fertilizer(temperature, humidity, moisture, soil_type, crop_type, nitrogen, potassium, phosphorous)
        return jsonify({'success': True, 'result': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test')
def api_test():
    """Simple test endpoint to verify API is working."""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'timestamp': pd.Timestamp.now().isoformat()
    })


@app.route('/api/predict-disease', methods=['POST'])
@app.route('/api/detect-disease', methods=['POST'])
def api_predict_disease():
    """API endpoint for classical CV + ML plant leaf disease diagnosis."""
    try:
        # Check if file uploaded via multipart form
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            img_bytes = file.read()
            if len(img_bytes) == 0:
                return jsonify({'success': False, 'error': 'Uploaded file is empty'}), 400
            if len(img_bytes) > 10 * 1024 * 1024:
                return jsonify({'success': False, 'error': 'File size exceeds maximum limit (10MB)'}), 400
                
            diagnosis = predict_disease(img_bytes)
            return jsonify({'success': True, 'result': diagnosis})

        # Or JSON base64 payload
        data = request.get_json(silent=True)
        if data and isinstance(data, dict) and 'image' in data:
            img_str = data.get('image', '').strip()
            if not img_str:
                return jsonify({'success': False, 'error': 'Image data cannot be empty'}), 400
            diagnosis = predict_disease(img_str)
            return jsonify({'success': True, 'result': diagnosis})

        return jsonify({'success': False, 'error': 'No image file or base64 image data provided'}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid image data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Disease diagnosis failed: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """RAG chatbot API endpoint."""
    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        message = str(data.get('message') or '').strip()
        session_id = str(data.get('session_id') or 'default').strip() or 'default'
        context = data.get('context')
        if not isinstance(context, dict):
            context = None

        if not message:
            return jsonify({"error": "Message is required"}), 400

        if len(message) > 500:
            return jsonify({"error": "Message too long. Keep under 500 characters."}), 400

        # Delegate to RAG chatbot backend (do not modify implementation there)
        result = chatbot_chat(message, session_id, context)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Chatbot error: {str(e)}"}), 500


# Load models at module level (so Gunicorn can access them)
print("[INFO] Initializing CropPulse web application...")
print(f"[INFO] Current working directory: {Path.cwd()}")
print(f"[INFO] MODEL_DIR: {MODEL_DIR}")
print(f"[INFO] Using Hugging Face repo: {HF_REPO_ID}")

print("[INFO] Loading ML models from Hugging Face Hub...")
try:
    load_models()
    print("[OK] All models loaded successfully!")
except Exception as e:
    print(f"[ERROR] Failed to load models: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway to allow health check and debugging


if __name__ == '__main__':
    import os
    
    # Get port from environment (for deployment platforms)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("Starting Flask development server...")
    app.run(debug=debug, host='0.0.0.0', port=port)

