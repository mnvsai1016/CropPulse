from dataclasses import dataclass
from pathlib import Path


@dataclass
class CropModelArtifact:
    model_path: Path
    nb_model_path: Path
    svm_model_path: Path
    scaler_path: Path
    encoder_path: Path


@dataclass
class YieldModelArtifact:
    model_path: Path
    scaler_path: Path
    columns_path: Path


@dataclass
class FertilizerModelTrainerArtifact:
    trained_model_file_path: str
    soil_encoder_file_path: str
    crop_encoder_file_path: str
    fertilizer_encoder_file_path: str
    model_accuracy: float








