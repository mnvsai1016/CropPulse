from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, r2_score, mean_absolute_error
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from agri_guide.entity import (
    CropModelArtifact,
    CropModelTrainerConfig,
    YieldModelArtifact,
    YieldModelTrainerConfig,
)
from agri_guide.exception import AgriGuideException
from agri_guide.logging import logger
from agri_guide.utils.main_utils import save_object


@dataclass
class CropTrainingResult:
    artifact: CropModelArtifact
    accuracy: float
    report: str


class CropModelTrainer:
    """Train and persist models for Module 1 (crop recommendation)."""

    def __init__(self, config: CropModelTrainerConfig | None = None) -> None:
        self.config = config or CropModelTrainerConfig()

    def train(
        self,
        X_train_fe,
        X_test_fe,
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
        scaler,
        label_encoder,
    ) -> CropTrainingResult:
        try:
            logger.info("Training GaussianNB, RandomForest, and SVM classifiers")

            nb_clf = GaussianNB()
            nb_clf.fit(X_train_scaled, y_train)

            rf_clf = RandomForestClassifier(
                n_estimators=100,  # Reduced from 200 for memory efficiency
                max_depth=20,      # Added depth limit for memory efficiency
                random_state=42,
                n_jobs=1,          # Reduced from -1 for memory efficiency
                max_features='sqrt',  # Use sqrt of features for efficiency
            )
            rf_clf.fit(X_train_fe, y_train)

            svm_clf = SVC(kernel="rbf", probability=True, random_state=42)
            svm_clf.fit(X_train_scaled, y_train)

            # Evaluate primary model (RandomForest)
            y_pred_rf = rf_clf.predict(X_test_fe)
            acc = accuracy_score(y_test, y_pred_rf)
            report = classification_report(y_test, y_pred_rf, target_names=label_encoder.classes_)

            logger.info("RandomForest accuracy: %.4f", acc)

            # Persist artifacts
            out_dir: Path = self.config.final_model_dir
            out_dir.mkdir(parents=True, exist_ok=True)

            rf_path = out_dir / self.config.rf_model_name
            nb_path = out_dir / self.config.nb_model_name
            svm_path = out_dir / self.config.svm_model_name
            scaler_path = out_dir / self.config.scaler_name
            encoder_path = out_dir / self.config.encoder_name

            save_object(rf_path, rf_clf)
            save_object(nb_path, nb_clf)
            save_object(svm_path, svm_clf)
            save_object(scaler_path, scaler)
            save_object(encoder_path, label_encoder)

            artifact = CropModelArtifact(
                model_path=rf_path,
                nb_model_path=nb_path,
                svm_model_path=svm_path,
                scaler_path=scaler_path,
                encoder_path=encoder_path,
            )

            return CropTrainingResult(artifact=artifact, accuracy=acc, report=report)
        except Exception as exc:  # pragma: no cover - orchestration
            raise AgriGuideException("Failed to train crop recommendation models", exc) from exc


@dataclass
class YieldTrainingResult:
    artifact: YieldModelArtifact
    r2: float
    mae: float


class YieldModelTrainer:
    """Train and persist models for Module 2 (yield prediction)."""

    def __init__(self, config: YieldModelTrainerConfig | None = None) -> None:
        self.config = config or YieldModelTrainerConfig()

    def train(
        self,
        X_train,
        X_test,
        y_train,
        y_test,
        scaler,
        feature_columns,
        state_encoder=None,
        season_encoder=None,
        crop_encoder=None,
    ) -> YieldTrainingResult:
        try:
            logger.info("Training memory-efficient RandomForestRegressor for yield prediction")

            # Reduced trees for memory efficiency (from 300 to 50)
            rf_reg = RandomForestRegressor(
                n_estimators=50,  # Reduced from 300 to save memory
                max_depth=15,     # Added depth limit for memory efficiency
                random_state=42,
                n_jobs=1,         # Reduced from -1 to save memory
                max_features='sqrt',  # Use sqrt of features for efficiency
            )
            rf_reg.fit(X_train, y_train)

            y_pred = rf_reg.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)

            logger.info("Yield RandomForestRegressor (optimized) R2=%.4f, MAE=%.4f", r2, mae)
            logger.info("Model uses %d trees with max_depth=%d for memory efficiency", 
                       rf_reg.n_estimators, rf_reg.max_depth)

            out_dir: Path = self.config.final_model_dir
            out_dir.mkdir(parents=True, exist_ok=True)

            model_path = out_dir / self.config.model_name
            scaler_path = out_dir / self.config.scaler_name
            columns_path = out_dir / self.config.columns_name
            state_encoder_path = out_dir / "yield_state_encoder.pkl"
            season_encoder_path = out_dir / "yield_season_encoder.pkl"
            crop_encoder_path = out_dir / "yield_crop_encoder.pkl"

            save_object(model_path, rf_reg)
            save_object(scaler_path, scaler)
            save_object(columns_path, feature_columns)
            
            # Save label encoders
            if state_encoder is not None:
                save_object(state_encoder_path, state_encoder)
                logger.info("Saved state encoder with %d classes", len(state_encoder.classes_))
            if season_encoder is not None:
                save_object(season_encoder_path, season_encoder)
                logger.info("Saved season encoder with %d classes", len(season_encoder.classes_))
            if crop_encoder is not None:
                save_object(crop_encoder_path, crop_encoder)
                logger.info("Saved crop encoder with %d classes", len(crop_encoder.classes_))

            artifact = YieldModelArtifact(
                model_path=model_path,
                scaler_path=scaler_path,
                columns_path=columns_path,
            )

            return YieldTrainingResult(artifact=artifact, r2=r2, mae=mae)
        except Exception as exc:  # pragma: no cover - orchestration
            raise AgriGuideException("Failed to train yield prediction model", exc) from exc








