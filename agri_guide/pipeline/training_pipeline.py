from agri_guide.components.data_ingestion import DataIngestion
from agri_guide.components.data_transformation import (
    ClassificationDataTransformer,
    RegressionDataTransformer,
)
from agri_guide.components.model_trainer import (
    CropModelTrainer,
    YieldModelTrainer,
)
from agri_guide.components.fertilizer_trainer import FertilizerModelTrainer
from agri_guide.logging import logger


class TrainingPipeline:
    """Orchestrates both Module 1 and Module 2 training pipelines."""

    def run_crop_recommendation(self) -> None:
        logger.info("=== Starting Module 1: Crop Recommendation Training ===")
        ingestion = DataIngestion()
        df_crop = ingestion.load_crop_recommendation()

        transformer = ClassificationDataTransformer()
        artifacts = transformer.transform(df_crop)

        trainer = CropModelTrainer()
        result = trainer.train(
            X_train_fe=artifacts.X_train_fe,
            X_test_fe=artifacts.X_test_fe,
            X_train_scaled=artifacts.X_train_scaled,
            X_test_scaled=artifacts.X_test_scaled,
            y_train=artifacts.y_train,
            y_test=artifacts.y_test,
            scaler=artifacts.scaler,
            label_encoder=artifacts.label_encoder,
        )

        logger.info("Module 1 training completed. Accuracy: %.4f", result.accuracy)
        logger.info("Classification report:\n%s", result.report)

    def run_yield_prediction(self) -> None:
        logger.info("=== Starting Module 2: Yield Prediction Training ===")
        ingestion = DataIngestion()
        df_prod = ingestion.load_crop_production()

        transformer = RegressionDataTransformer()
        artifacts = transformer.transform(df_prod)

        trainer = YieldModelTrainer()
        result = trainer.train(
            X_train=artifacts.X_train,
            X_test=artifacts.X_test,
            y_train=artifacts.y_train,
            y_test=artifacts.y_test,
            scaler=artifacts.scaler,
            feature_columns=artifacts.feature_columns,
            state_encoder=artifacts.state_encoder,
            season_encoder=artifacts.season_encoder,
            crop_encoder=artifacts.crop_encoder,
        )

        logger.info("Module 2 training completed. R2=%.4f, MAE=%.4f", result.r2, result.mae)

    def run_fertilizer_prediction(self) -> None:
        logger.info("=== Starting Module 3: Fertilizer Prediction Training ===")
        ingestion = DataIngestion()
        df_fertilizer = ingestion.load_fertilizer_data()

        trainer = FertilizerModelTrainer()
        result = trainer.train(df_fertilizer)

        logger.info("Module 3 training completed. Accuracy: %.4f", result.model_accuracy)








