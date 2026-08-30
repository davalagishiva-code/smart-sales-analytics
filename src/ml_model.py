"""Machine learning utilities: train, evaluate, save/load model pipeline.

This module trains a regression model to predict `Sales` for an order item
using features such as Quantity, Unit Price, Discount, Category, Region, and Payment Method.
The trained object is a scikit-learn Pipeline saved with joblib for later use by the Flask app.
"""
from typing import Tuple, Dict, Any
import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

MODEL_PATH = os.path.join('models', 'sales_model.pkl')


def _get_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Select features and target from cleaned DataFrame."""
    df = df.copy()
    # Ensure required columns exist
    required = ['Quantity', 'Unit Price', 'Discount', 'Category', 'Region', 'Payment Method', 'Sales']
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Required column missing: {c}")

    X = df[['Quantity', 'Unit Price', 'Discount', 'Category', 'Region', 'Payment Method']].copy()
    y = df['Sales'].astype(float).copy()
    # Fill numeric NaNs
    X['Quantity'] = pd.to_numeric(X['Quantity'], errors='coerce').fillna(1)
    X['Unit Price'] = pd.to_numeric(X['Unit Price'], errors='coerce').fillna(X['Unit Price'].median())
    X['Discount'] = pd.to_numeric(X['Discount'], errors='coerce').fillna(0.0)
    X[['Category','Region','Payment Method']] = X[['Category','Region','Payment Method']].fillna('Unknown')
    return X, y


def build_pipeline() -> Pipeline:
    """Create preprocessing + model pipeline."""
    numeric_features = ['Quantity', 'Unit Price', 'Discount']
    numeric_transformer = StandardScaler()

    categorical_features = ['Category', 'Region', 'Payment Method']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features),
        ]
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    return pipeline


def train_and_evaluate(df: pd.DataFrame, model_path: str = MODEL_PATH, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
    """Train model pipeline and evaluate on test set. Saves pipeline to `model_path`.

    Returns a dictionary with evaluation metrics.
    """
    X, y = _get_features_and_target(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    pipeline = build_pipeline()
    log.info('Training model...')
    pipeline.fit(X_train, y_train)

    # Evaluate
    preds = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_test, preds)

    metrics = {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'test_size': test_size
    }

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    log.info(f'Saved trained model to {model_path}')

    # Save metrics alongside model
    metrics_path = model_path + '.metrics.json'
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    log.info(f'Saved metrics to {metrics_path}')

    return metrics


def load_model(path: str = MODEL_PATH) -> Pipeline:
    if not os.path.exists(path):
        raise FileNotFoundError(f'Model file not found: {path}')
    return joblib.load(path)


def predict_from_dict(model: Pipeline, data: Dict[str, Any]) -> float:
    """Predict sales for a single input dictionary of features.

    Example input keys: 'Quantity', 'Unit Price', 'Discount', 'Category', 'Region', 'Payment Method'
    """
    df = pd.DataFrame([data])
    # Ensure same preprocessing expectations
    for col in ['Quantity', 'Unit Price', 'Discount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    for col in ['Category', 'Region', 'Payment Method']:
        if col not in df.columns:
            df[col] = 'Unknown'
    pred = model.predict(df)[0]
    return float(pred)

