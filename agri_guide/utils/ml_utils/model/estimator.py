from dataclasses import dataclass
from typing import Any

from sklearn.base import ClassifierMixin, RegressorMixin


@dataclass
class CropClassifier:
    """Wrapper for the crop recommendation classifier artifacts."""

    model: ClassifierMixin
    scaler: Any
    label_encoder: Any


@dataclass
class YieldRegressor:
    """Wrapper for the yield prediction regressor artifacts."""

    model: RegressorMixin
    scaler: Any
    feature_columns: list[str]








