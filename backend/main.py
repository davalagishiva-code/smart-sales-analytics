from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.analytics import generate_analysis_payload
from src.database import (
    DB_PATH,
    add_sale,
    create_customer,
    create_product,
    delete_customer,
    delete_product,
    delete_sale,
    fetch_sales,
    get_categories,
    get_customer_by_id,
    get_customer_purchase_history,
    get_customer_segments,
    get_customer_summary,
    get_customers,
    get_dashboard_metrics,
    get_database_summary,
    get_products,
    get_recent_customers,
    get_sales_for_ml,
    get_top_customers,
    initialize_database,
    update_customer,
    update_product,
)
from src.ml_model import ensure_model_exists, predict_sale_amount

BASE_DIR = Path(__file__).resolve().parent.parent


class SaleCreate(BaseModel):
    date: str
    product: str
    category: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(default=0.0, ge=0, le=100)
    customer: str
    region: str
    payment_method: str

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        from datetime import datetime

        try:
            datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Date must be a valid ISO date string.") from exc
        return value

    @field_validator("product", "category", "customer", "region", "payment_method")
    @classmethod
    def clean_strings(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field is required.")
        return cleaned


class PredictionInput(BaseModel):
    date: str
    product: str
    category: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(default=0.0, ge=0, le=100)
    customer: str
    region: str
    payment_method: str


class CustomerInput(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    customer_type: str = "Regular"
    status: str = "Active"
    registration_date: Optional[str] = None

    @field_validator("name", "email", "phone", "address", "city", "state", "pincode", "customer_type", "status")
    @classmethod
    def clean_strings(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field is required.")
        return cleaned


class ProductInput(BaseModel):
    name: str
    sku: Optional[str] = None
    category: str = "Uncategorized"
    price: float = Field(..., gt=0)
    cost_price: float = Field(default=0.0, ge=0)
    stock: int = Field(default=0, ge=0)
    min_stock: int = Field(default=0, ge=0)
    description: str = ""
    status: Optional[str] = "active"

    @field_validator("name", "category")
    @classmethod
    def clean_strings(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field is required.")
        return cleaned

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


app = FastAPI(
    title="Smart Sales Analytics",
    description="Professional sales analytics and prediction platform built with FastAPI.",
    version="1.0.0",
)

allowed_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
]
production_url = os.getenv("NETLIFY_FRONTEND_URL")
if production_url:
    allowed_origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    initialize_database()
    ensure_model_exists(get_sales_for_ml())


@app.get("/")
def root() -> Dict[str, Any]:
    return {"application": "Smart Sales Analytics", "status": "running"}


@app.get("/health")
def health_check() -> Dict[str, Any]:
    try:
        summary = get_database_summary()
        return {
            "status": "ok",
            "database": "ready",
            "database_path": summary["database_path"],
            "records": summary["total_records"],
        }
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(exc)}") from exc


@app.get("/api/dashboard")
def get_dashboard(
    range: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    filter_payload: Dict[str, Any] = {}
    today = datetime.date.today()

    if start_date:
        filter_payload["start_date"] = start_date
    if end_date:
        filter_payload["end_date"] = end_date

    selected_range = range or "all"

    if selected_range and selected_range != "all":
        if selected_range == "today":
            start_date_value = today.isoformat()
            end_date_value = today.isoformat()
        elif selected_range == "week":
            start_date_value = (today - datetime.timedelta(days=7)).isoformat()
            end_date_value = today.isoformat()
        elif selected_range == "month":
            start_date_value = today.replace(day=1).isoformat()
            end_date_value = today.isoformat()
        elif selected_range == "last_month":
            first_day = today.replace(day=1)
            last_month = first_day - datetime.timedelta(days=1)
            start_date_value = last_month.replace(day=1).isoformat()
            end_date_value = last_month.isoformat()
        elif selected_range == "year":
            start_date_value = today.replace(month=1, day=1).isoformat()
            end_date_value = today.isoformat()
        else:
            start_date_value = None
            end_date_value = None

        if selected_range in {"today", "week", "month", "year", "last_month"}:
            filter_payload["start_date"] = start_date_value
            filter_payload["end_date"] = end_date_value

    metrics = get_dashboard_metrics(filter_payload)
    return {
        "message": "Sales dashboard data loaded",
        "metrics": metrics,
        "data": metrics,
        "filters": {
            "range": selected_range,
            "start_date": filter_payload.get("start_date"),
            "end_date": filter_payload.get("end_date"),
        },
    }


@app.get("/api/analysis")
def get_analysis(
    range: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
) -> Dict[str, Any]:
    today = datetime.date.today()
    applied_start = start_date
    applied_end = end_date

    if range and range != "all":
        if range == "today":
            applied_start = today.isoformat()
            applied_end = today.isoformat()
        elif range == "week":
            applied_start = (today - datetime.timedelta(days=7)).isoformat()
            applied_end = today.isoformat()
        elif range == "month":
            applied_start = today.replace(day=1).isoformat()
            applied_end = today.isoformat()
        elif range == "last_month":
            first_day = today.replace(day=1)
            last_month = first_day - datetime.timedelta(days=1)
            applied_start = last_month.replace(day=1).isoformat()
            applied_end = last_month.isoformat()
        elif range == "year":
            applied_start = today.replace(month=1, day=1).isoformat()
            applied_end = today.isoformat()

    sales = fetch_sales({
        "start_date": applied_start,
        "end_date": applied_end,
        "category": category,
        "region": region,
        "payment_method": payment_method,
    })
    analysis = generate_analysis_payload(sales, {
        "start_date": applied_start,
        "end_date": applied_end,
        "category": category,
        "region": region,
        "payment_method": payment_method,
    })
    return {"message": "Analysis data loaded", "filters": {
        "range": range,
        "start_date": applied_start,
        "end_date": applied_end,
        "category": category,
        "region": region,
        "payment_method": payment_method,
    }, "data": analysis}


@app.get("/api/sales")
def get_sales_list(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(default="date"),
    order: Optional[str] = Query(default="desc"),
) -> Dict[str, Any]:
    payload = {
        "search": search,
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
    }
    sales = fetch_sales(payload)
    if sort_by == "total_amount":
        sales = sorted(sales, key=lambda item: float(item.get("total_amount", 0) or 0), reverse=(order.lower() != "asc"))
    elif sort_by == "product":
        sales = sorted(sales, key=lambda item: str(item.get("product", "")).lower(), reverse=(order.lower() != "asc"))
    else:
        sales = sorted(sales, key=lambda item: item.get("date", ""), reverse=(order.lower() != "asc"))
    return {"message": "Sales records retrieved", "data": sales}


@app.post("/api/sales", status_code=201)
def create_sale(sale: SaleCreate) -> Dict[str, Any]:
    try:
        record = add_sale(sale.model_dump())
        return {"message": "Sale saved successfully", "data": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to save sale: {str(exc)}") from exc


@app.delete("/api/sales/{sale_id}")
def delete_sale_record(sale_id: int) -> Dict[str, Any]:
    deleted = delete_sale(sale_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale not found.")
    return {"message": "Sale deleted successfully", "sale_id": sale_id}


@app.get("/api/categories")
def categories() -> Dict[str, Any]:
    return {"message": "Categories loaded", "data": get_categories()}


@app.get("/api/products")
def products() -> Dict[str, Any]:
    rows = get_products()
    return {"message": "Product catalog loaded", "data": rows}


@app.post("/api/products", status_code=201)
def create_product_route(payload: ProductInput) -> Dict[str, Any]:
    try:
        record = create_product(payload.model_dump())
        return {"message": "Product created successfully", "data": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(exc)}") from exc


@app.put("/api/products/{product_id}")
def update_product_route(product_id: int, payload: ProductInput) -> Dict[str, Any]:
    try:
        record = update_product(product_id, payload.model_dump())
        if record is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        return {"message": "Product updated successfully", "data": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(exc)}") from exc


@app.delete("/api/products/{product_id}")
def delete_product_route(product_id: int) -> Dict[str, Any]:
    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found.")
    return {"message": "Product deleted successfully", "deleted": True, "product_id": product_id}


@app.get("/api/customers")
def customers() -> Dict[str, Any]:
    rows = get_customers()
    stats = get_customer_summary()
    segments = get_customer_segments()
    return {
        "message": "Customer data loaded",
        "data": rows,
        "stats": stats,
        "segments": segments,
        "top_customers": get_top_customers(5),
        "recent_customers": get_recent_customers(5),
    }


@app.get("/api/customers/{customer_id}")
def get_customer_detail(customer_id: int) -> Dict[str, Any]:
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"message": "Customer loaded", "data": customer}


@app.post("/api/customers", status_code=201)
def create_customer_route(payload: CustomerInput) -> Dict[str, Any]:
    try:
        record = create_customer(payload.model_dump())
        return {"message": "Customer added successfully", "data": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(exc)}") from exc


@app.put("/api/customers/{customer_id}")
def update_customer_route(customer_id: int, payload: CustomerInput) -> Dict[str, Any]:
    try:
        record = update_customer(customer_id, payload.model_dump())
        if record is None:
            raise HTTPException(status_code=404, detail="Customer not found.")
        return {"message": "Customer updated successfully", "data": record}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to update customer: {str(exc)}") from exc


@app.delete("/api/customers/{customer_id}")
def delete_customer_route(customer_id: int) -> Dict[str, Any]:
    deleted = delete_customer(customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"message": "Customer deleted successfully", "deleted": True, "customer_id": customer_id}


@app.get("/api/customers/{customer_id}/sales")
def customer_sales_history(customer_id: int) -> Dict[str, Any]:
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return {"message": "Purchase history loaded", "data": customer.get("purchases", [])}


@app.post("/api/predict")
def predict_route(payload: PredictionInput) -> Dict[str, Any]:
    try:
        model_data = get_sales_for_ml()
        prediction = predict_sale_amount(payload.model_dump(), model_data)
        return {
            "message": "Prediction generated successfully",
            "input": payload.model_dump(),
            "prediction": prediction,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}") from exc


@app.get("/api/reports")
def reports() -> Dict[str, Any]:
    sales = fetch_sales({})
    return {"message": "Reports data loaded", "data": sales}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8080, reload=True)
