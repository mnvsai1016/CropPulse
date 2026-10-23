from pathlib import Path

import pandas as pd

from agri_guide.entity import DataIngestionConfig
from agri_guide.exception import AgriGuideException
from agri_guide.logging import logger


class DataIngestion:
    """Load raw datasets required by the Agri-Guide system."""

    def __init__(self, config: DataIngestionConfig | None = None) -> None:
        self.config = config or DataIngestionConfig()

    def load_crop_recommendation(self) -> pd.DataFrame:
        """Load the crop recommendation dataset into a DataFrame."""
        try:
            path: Path = self.config.crop_recommendation_path
            logger.info("Loading crop recommendation data from %s", path)
            return pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - I/O wrapper
            raise AgriGuideException("Failed to load crop recommendation data", exc) from exc

    def load_crop_production(self) -> pd.DataFrame:
        """Load the crop production dataset into a DataFrame."""
        try:
            path: Path = self.config.crop_production_path
            logger.info("Loading crop production data from %s", path)
            return pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - I/O wrapper
            raise AgriGuideException("Failed to load crop production data", exc) from exc

    def load_fertilizer_data(self) -> pd.DataFrame:
        """Load the fertilizer prediction dataset into a DataFrame."""
        try:
            path: Path = Path("Fertilizer_Prediction.csv")
            logger.info("Loading fertilizer data from %s", path)
            return pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - I/O wrapper
            raise AgriGuideException("Failed to load fertilizer data", exc) from exc








