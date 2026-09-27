from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "sales_model.pkl"


def _build_value_map(values: List[str]) -> Dict[str, int]:
    unique_values = sorted({str(value).strip().lower() for value in values if str(value).strip()})
    return {value: index for index, value in enumerate(unique_values)}


def _prepare_training_data(sales: List[Dict[str, Any]]) -> Optional[pd.DataFrame]:
    if not sales:
        return None

    records = []
    for sale in sales:
        records.append({
            "quantity": float(sale.get("quantity", 0) or 0),
            "unit_price": float(sale.get("unit_price", 0) or 0),
            "discount": float(sale.get("discount", 0) or 0),
            "total_amount": float(sale.get("total_amount", 0) or 0),
            "product": str(sale.get("product", "")).lower(),
            "category": str(sale.get("category", "")).lower(),
            "customer": str(sale.get("customer", "")).lower(),
            "region": str(sale.get("region", "")).lower(),
            "payment_method": str(sale.get("payment_method", "")).lower(),
        })

    df = pd.DataFrame(records)
    if df.empty or len(df) < 2:
        return None

    product_map = _build_value_map(df["product"].tolist())
    category_map = _build_value_map(df["category"].tolist())
    customer_map = _build_value_map(df["customer"].tolist())
    region_map = _build_value_map(df["region"].tolist())
    payment_map = _build_value_map(df["payment_method"].tolist())

    df["product_code"] = df["product"].map(product_map).fillna(0).astype(int)
    df["category_code"] = df["category"].map(category_map).fillna(0).astype(int)
    df["customer_code"] = df["customer"].map(customer_map).fillna(0).astype(int)
    df["region_code"] = df["region"].map(region_map).fillna(0).astype(int)
    df["payment_code"] = df["payment_method"].map(payment_map).fillna(0).astype(int)

    return df[["quantity", "unit_price", "discount", "product_code", "category_code", "customer_code", "region_code", "payment_code", "total_amount"]]


def _build_model() -> Any:
    return RandomForestRegressor(n_estimators=200, random_state=42)


def ensure_model_exists(sales: List[Dict[str, Any]]) -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if len(sales) < 2:
        if MODEL_PATH.exists():
            return
        joblib.dump({"is_ready": False, "message": "Not enough sales data to train model."}, MODEL_PATH)
        return

    df = _prepare_training_data(sales)
    if df is None or len(df) < 2:
        if MODEL_PATH.exists():
            return
        joblib.dump({"is_ready": False, "message": "Not enough sales data to train model."}, MODEL_PATH)
        return

    X = df.drop(columns=["total_amount"])
    y = df["total_amount"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = _build_model()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    score = mean_squared_error(y_test, predictions)
    payload = {
        "is_ready": True,
        "model": model,
        "feature_columns": list(X.columns),
        "value_maps": {
            "product": _build_value_map(sales[0].get("product", "") if len(sales) == 1 else [str(item.get("product", "")).lower() for item in sales]),
            "category": _build_value_map([str(item.get("category", "")).lower() for item in sales]),
            "customer": _build_value_map([str(item.get("customer", "")).lower() for item in sales]),
            "region": _build_value_map([str(item.get("region", "")).lower() for item in sales]),
            "payment_method": _build_value_map([str(item.get("payment_method", "")).lower() for item in sales]),
        },
        "score": float(score),
        "trained_records": len(df),
    }
    joblib.dump(payload, MODEL_PATH)


def predict_sale_amount(payload: Dict[str, Any], sales: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    data = sales if sales is not None else []
    model_file = MODEL_PATH
    if not model_file.exists():
        ensure_model_exists(data)
    if not model_file.exists():
        raise ValueError("No trained model exists yet. Add more sales data first.")

    loaded = joblib.load(model_file)
    if not loaded.get("is_ready"):
        raise ValueError(loaded.get("message", "Insufficient sales data available for a prediction model."))

    model = loaded["model"]
    feature_columns = loaded["feature_columns"]
    value_maps = loaded.get("value_maps", {})

    product = str(payload.get("product", "")).lower()
    category = str(payload.get("category", "")).lower()
    customer = str(payload.get("customer", "")).lower()
    region = str(payload.get("region", "")).lower()
    payment_method = str(payload.get("payment_method", "")).lower()

    row = {
        "quantity": float(payload.get("quantity") or 0),
        "unit_price": float(payload.get("unit_price") or 0),
        "discount": float(payload.get("discount") or 0),
        "product_code": value_maps.get("product", {}).get(product, 0),
        "category_code": value_maps.get("category", {}).get(category, 0),
        "customer_code": value_maps.get("customer", {}).get(customer, 0),
        "region_code": value_maps.get("region", {}).get(region, 0),
        "payment_code": value_maps.get("payment_method", {}).get(payment_method, 0),
    }

    ordered = [row.get(feature, 0.0) for feature in feature_columns]
    prediction = float(model.predict(np.array([ordered]))[0])
    return {
        "predicted_total_amount": round(max(prediction, 0), 2),
        "confidence": "model-based estimate",
        "training_records": loaded.get("trained_records", 0),
        "model_score": loaded.get("score"),
    }
