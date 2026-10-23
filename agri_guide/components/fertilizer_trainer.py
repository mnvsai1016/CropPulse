import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
from pathlib import Path

from agri_guide.logging import logger
from agri_guide.entity.config_entity import FertilizerModelTrainerConfig
from agri_guide.entity.artifact_entity import FertilizerModelTrainerArtifact


class FertilizerModelTrainer:
    """Trains Support Vector Classifier (SVC) model for fertilizer prediction."""

    def __init__(self, config: FertilizerModelTrainerConfig = None):
        self.config = config or FertilizerModelTrainerConfig()

    def train(self, df: pd.DataFrame) -> FertilizerModelTrainerArtifact:
        """Train fertilizer prediction model using Support Vector Machine (SVC)."""
        try:
            logger.info("Starting fertilizer model training (Support Vector Classifier)")
            
            # Prepare features and target
            feature_columns = ['Temparature', 'Humidity ', 'Moisture', 'Soil Type', 
                             'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous']
            target_column = 'Fertilizer Name'
            
            X = df[feature_columns].copy()
            y = df[target_column].copy()
            
            # Clean column names (remove extra spaces)
            X.columns = X.columns.str.strip()
            
            # Encode categorical variables
            soil_encoder = LabelEncoder()
            crop_encoder = LabelEncoder()
            fertilizer_encoder = LabelEncoder()
            
            X['Soil Type'] = soil_encoder.fit_transform(X['Soil Type'])
            X['Crop Type'] = crop_encoder.fit_transform(X['Crop Type'])
            y_encoded = fertilizer_encoder.fit_transform(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Train Support Vector Classifier with StandardScaler in Pipeline
            model = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', SVC(
                    kernel='linear',
                    C=0.5,
                    probability=True,
                    random_state=42
                ))
            ])
            
            model.fit(X_train.values, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Fertilizer model accuracy: {accuracy:.4f}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
            
            # Save model and encoders
            model_path = Path(self.config.trained_model_file_path)
            soil_encoder_path = Path(self.config.soil_encoder_file_path)
            crop_encoder_path = Path(self.config.crop_encoder_file_path)
            fertilizer_encoder_path = Path(self.config.fertilizer_encoder_file_path)
            
            # Create directories if they don't exist
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(soil_encoder_path, 'wb') as f:
                pickle.dump(soil_encoder, f)
                
            with open(crop_encoder_path, 'wb') as f:
                pickle.dump(crop_encoder, f)
                
            with open(fertilizer_encoder_path, 'wb') as f:
                pickle.dump(fertilizer_encoder, f)
            
            logger.info(f"Fertilizer model saved to: {model_path}")
            
            return FertilizerModelTrainerArtifact(
                trained_model_file_path=str(model_path),
                soil_encoder_file_path=str(soil_encoder_path),
                crop_encoder_file_path=str(crop_encoder_path),
                fertilizer_encoder_file_path=str(fertilizer_encoder_path),
                model_accuracy=accuracy
            )
            
        except Exception as e:
            logger.error(f"Error in fertilizer model training: {e}")
            raise e