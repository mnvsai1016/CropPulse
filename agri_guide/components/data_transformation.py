from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA

from agri_guide.exception import AgriGuideException
from agri_guide.logging import logger


CLASS_NUMERIC_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def _add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    df_fe = df.copy()
    df_fe["NPK_sum"] = df_fe["N"] + df_fe["P"] + df_fe["K"]
    df_fe["N_K_ratio"] = df_fe["N"] / (df_fe["K"] + 1e-3)
    df_fe["temp_humidity_index"] = df_fe["temperature"] * df_fe["humidity"] / 100.0
    df_fe["is_acidic"] = (df_fe["ph"] < 7).astype(int)
    df_fe["rainfall_per_NPK"] = df_fe["rainfall"] / (df_fe["NPK_sum"] + 1e-3)
    return df_fe


@dataclass
class ClassificationTransformArtifacts:
    X_train_fe: np.ndarray
    X_test_fe: np.ndarray
    X_train_scaled: np.ndarray
    X_test_scaled: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    scaler: StandardScaler
    label_encoder: LabelEncoder


class ClassificationDataTransformer:
    """Preprocess Module 1 data: outliers, feature engineering, splits, scaling."""

    def transform(self, df: pd.DataFrame) -> ClassificationTransformArtifacts:
        try:
            logger.info("Starting classification data transformation")

            # IQR-based clipping on numeric features
            df_num = df.copy()
            for col in CLASS_NUMERIC_COLS:
                Q1 = df_num[col].quantile(0.25)
                Q3 = df_num[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR == 0:
                    continue
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                df_num[col] = df_num[col].clip(lower=lower, upper=upper)

            X = df_num[CLASS_NUMERIC_COLS].copy()
            y = df_num["label"].copy()

            le = LabelEncoder()
            y_encoded = le.fit_transform(y)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )

            X_train_fe = _add_engineered_features(X_train)
            X_test_fe = _add_engineered_features(X_test)

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train_fe)
            X_test_scaled = scaler.transform(X_test_fe)

            return ClassificationTransformArtifacts(
                X_train_fe=X_train_fe.values,
                X_test_fe=X_test_fe.values,
                X_train_scaled=X_train_scaled,
                X_test_scaled=X_test_scaled,
                y_train=y_train,
                y_test=y_test,
                scaler=scaler,
                label_encoder=le,
            )
        except Exception as exc:  # pragma: no cover - orchestration
            raise AgriGuideException("Failed to transform classification data", exc) from exc


@dataclass
class RegressionTransformArtifacts:
    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    scaler: StandardScaler
    feature_columns: list[str]
    state_encoder: LabelEncoder
    season_encoder: LabelEncoder
    crop_encoder: LabelEncoder


class RegressionDataTransformer:
    """Preprocess Module 2 data: cleaning, yield computation, encoding, scaling."""

    def transform(self, df_prod_raw: pd.DataFrame) -> RegressionTransformArtifacts:
        try:
            logger.info("Starting regression data transformation")

            # Drop rows with missing production and non-positive area
            df_prod = df_prod_raw.dropna(subset=["Production"]).copy()
            df_prod = df_prod.loc[df_prod["Area"] > 0].copy()

            # Outlier trimming for Area and Production
            for col in ["Area", "Production"]:
                Q1 = df_prod[col].quantile(0.25)
                Q3 = df_prod[col].quantile(0.75)
                IQR = Q3 - Q1
                before = df_prod.shape[0]

                if IQR == 0:
                    upper_bound = df_prod[col].quantile(0.99)
                    lower_bound = 0 if col == "Production" else df_prod[col].quantile(0.01)
                else:
                    lower_bound = max(0, Q1 - 1.5 * IQR)
                    upper_bound = Q3 + 1.5 * IQR

                df_prod = df_prod[
                    (df_prod[col] >= lower_bound) & (df_prod[col] <= upper_bound)
                ]
                after = df_prod.shape[0]
                logger.info("%s: removed %d rows as outliers", col, before - after)

            # Yield computation
            df_prod["Yield"] = df_prod["Production"] / df_prod["Area"]
            df_prod = df_prod[np.isfinite(df_prod["Yield"])].copy()

            # Yield outlier handling (percentile + hard cap)
            p_high = df_prod["Yield"].quantile(0.995)
            max_reasonable_yield = min(p_high, 20.0)
            df_prod = df_prod.loc[df_prod["Yield"] <= max_reasonable_yield].copy()

            # Feature selection (exclude Crop_Year from model)
            cols_to_use = ["State_Name", "Season", "Crop", "Area", "Yield"]
            df_model = df_prod[cols_to_use].copy()

            X = df_model.drop("Yield", axis=1)
            y = df_model["Yield"].copy()

            # Use Label Encoding instead of One-Hot Encoding for memory efficiency
            state_encoder = LabelEncoder()
            season_encoder = LabelEncoder()
            crop_encoder = LabelEncoder()
            
            X_encoded = X.copy()
            X_encoded["State_Name"] = state_encoder.fit_transform(X["State_Name"])
            X_encoded["Season"] = season_encoder.fit_transform(X["Season"])
            X_encoded["Crop"] = crop_encoder.fit_transform(X["Crop"])
            
            logger.info(f"Label encoding: {len(state_encoder.classes_)} states, {len(season_encoder.classes_)} seasons, {len(crop_encoder.classes_)} crops")

            # Scale Area feature
            scaler = StandardScaler()
            X_encoded["Area"] = scaler.fit_transform(X_encoded[["Area"]])

            from sklearn.model_selection import train_test_split as _tts

            X_train, X_test, y_train, y_test = _tts(
                X_encoded, y, test_size=0.2, random_state=42
            )

            feature_columns = ["State_Name", "Season", "Crop", "Area"]
            
            logger.info(f"Final features: {len(feature_columns)} (much more memory efficient than one-hot encoding)")

            return RegressionTransformArtifacts(
                X_train=X_train.values,
                X_test=X_test.values,
                y_train=y_train.values,
                y_test=y_test.values,
                scaler=scaler,
                feature_columns=feature_columns,
                state_encoder=state_encoder,
                season_encoder=season_encoder,
                crop_encoder=crop_encoder,
            )
        except Exception as exc:  # pragma: no cover - orchestration
            raise AgriGuideException("Failed to transform regression data", exc) from exc








