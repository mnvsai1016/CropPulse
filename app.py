from agri_guide.logging import logger
from agri_guide.pipeline.training_pipeline import TrainingPipeline


def main() -> None:
    pipeline = TrainingPipeline()

    # Train all modules sequentially
    pipeline.run_crop_recommendation()
    pipeline.run_yield_prediction()
    pipeline.run_fertilizer_prediction()


if __name__ == "__main__":
    logger.info("Starting Agri-Guide training run from app.py")
    main()








