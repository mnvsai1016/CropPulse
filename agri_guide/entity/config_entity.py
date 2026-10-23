from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataIngestionConfig:
    crop_recommendation_path: Path = Path("raw_data/Crop_recommendation.csv")
    crop_production_path: Path = Path("raw_data/crop_production.csv")


@dataclass
class CropModelTrainerConfig:
    final_model_dir: Path = Path("final_model")
    rf_model_name: str = "crop_recommendation_model.pkl"
    nb_model_name: str = "crop_recommendation_nb.pkl"
    svm_model_name: str = "crop_recommendation_svm.pkl"
    scaler_name: str = "scaler.pkl"
    encoder_name: str = "label_encoder.pkl"


@dataclass
class YieldModelTrainerConfig:
    final_model_dir: Path = Path("final_model")
    model_name: str = "yield_model.pkl"
    scaler_name: str = "yield_scaler.pkl"
    columns_name: str = "yield_feature_columns.pkl"


@dataclass
class FertilizerModelTrainerConfig:
    final_model_dir: Path = Path("final_model")
    trained_model_file_path: str = "final_model/fertilizer_model.pkl"
    soil_encoder_file_path: str = "final_model/soil_encoder.pkl"
    crop_encoder_file_path: str = "final_model/crop_encoder.pkl"
    fertilizer_encoder_file_path: str = "final_model/fertilizer_encoder.pkl"








