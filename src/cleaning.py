"""Data cleaning and ETL utilities for Smart Sales Analytics.

Provides functions to:
- load raw CSV(s)
- detect and report missing values
- remove duplicates
- convert and normalize types (dates, numeric)
- detect simple outliers (IQR)
- engineer helpful columns (Year, Month, YearMonth)
- save cleaned CSV
- optionally load cleaned data into MySQL (split into tables)

Usage (CLI):
    python -m src.cleaning --input data/raw_sales.csv --out data/cleaned_sales.csv --load-db

The module uses environment variables for DB credentials when loading to MySQL.
"""
from typing import List, Tuple
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import logging

load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def read_csv(path: str) -> pd.DataFrame:
    """Read CSV into DataFrame with safe defaults."""
    try:
        df = pd.read_csv(path, dtype=str)
        log.info(f"Loaded {len(df)} rows from {path}")
        return df
    except Exception as e:
        log.error(f"Failed to read CSV {path}: {e}")
        raise


def report_missing(df: pd.DataFrame) -> pd.Series:
    """Return count of missing values per column."""
    miss = df.isna().sum()
    log.info(f"Missing values:\n{miss[miss>0]}")
    return miss


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """Drop duplicate rows. By default uses all columns."""
    before = len(df)
    df2 = df.drop_duplicates(subset=subset)
    log.info(f"Removed {before - len(df2)} duplicate rows")
    return df2


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric and date-like columns to proper dtypes."""
    df = df.copy()
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Convert dates
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

    # Numeric conversions
    for col in ['Quantity', 'Unit Price', 'Discount', 'Sales', 'Profit']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Simple, transparent missing-value handling:
    - Drop rows missing `Order ID` or `Order Date`.
    - Fill numeric NaNs with column median.
    - Fill categorical NaNs with 'Unknown'.
    """
    df = df.copy()
    # Mandatory fields
    if 'Order ID' in df.columns:
        df = df[df['Order ID'].notna()]
    if 'Order Date' in df.columns:
        df = df[df['Order Date'].notna()]

    # Numeric fill
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        median = df[col].median()
        df[col] = df[col].fillna(median)

    # Categorical fill
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in categorical_cols:
        df[col] = df[col].fillna('Unknown')

    return df


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> Tuple[pd.Series, float, float]:
    """Detect outliers using the IQR rule. Returns boolean mask and (low, high) bounds."""
    if column not in df.columns:
        raise ValueError(f"Column {column} not in DataFrame")
    series = df[column].dropna().astype(float)
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    low = q1 - factor * iqr
    high = q3 + factor * iqr
    mask = (df[column] < low) | (df[column] > high)
    log.info(f"Outlier bounds for {column}: low={low}, high={high}; outliers={mask.sum()}")
    return mask, low, high


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add Year, Month, YearMonth, and normalize discount as fraction."""
    df = df.copy()
    if 'Order Date' in df.columns:
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
        df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

    # Ensure discount is fraction (e.g., 0.05)
    if 'Discount' in df.columns:
        # some inputs may provide percentage like '5' meaning 5% -> convert heuristic
        df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
        df.loc[df['Discount'] > 1, 'Discount'] = df.loc[df['Discount'] > 1, 'Discount'] / 100.0

    # Compute Sales if missing
    if not df.get('Sales').any():
        if all(c in df.columns for c in ['Quantity', 'Unit Price', 'Discount']):
            df['Sales'] = (df['Quantity'] * df['Unit Price'] * (1 - df['Discount'])).round(2)

    return df


def save_cleaned(df: pd.DataFrame, out_path: str) -> None:
    """Save cleaned dataframe to CSV."""
    df.to_csv(out_path, index=False)
    log.info(f"Saved cleaned data to {out_path} ({len(df)} rows)")


def create_db_engine_from_env() -> 'Engine':
    """Create SQLAlchemy engine using environment variables loaded from .env or OS."""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.engine import Engine
    except ImportError as e:
        raise ImportError('SQLAlchemy is required to load data into MySQL. Install it with `pip install sqlalchemy`.') from e

    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASS')
    host = os.environ.get('DB_HOST', 'localhost')
    db = os.environ.get('DB_NAME')
    if not all([user, password, db]):
        raise EnvironmentError('DB_USER, DB_PASS, and DB_NAME must be set in environment to load to DB')
    url = f"mysql+mysqlconnector://{user}:{password}@{host}/{db}"
    engine = create_engine(url)
    return engine


def load_flat_to_db(df: pd.DataFrame, engine, if_exists: str = 'append') -> None:
    """Load a flattened sales CSV into normalized MySQL tables.

    This function splits the flat CSV into `regions`, `customers`, `products`, `orders`, and `order_items`.
    It writes to the database using `to_sql`. Primary key and FK constraints are expected in the schema.
    """
    # Regions
    regions = df[['Region']].drop_duplicates().rename(columns={'Region': 'name'})
    regions.to_sql('regions', engine, if_exists=if_exists, index=False)

    # Customers (map region to region_id is left to DB via join or manual mapping)
    customers = df[['Customer ID', 'Customer Name', 'Region']].drop_duplicates()
    customers = customers.rename(columns={'Customer ID': 'customer_id', 'Customer Name': 'customer_name'})
    # Write customers (region_id nullable) - recommend post-process in DB to map region ids
    customers[['customer_id', 'customer_name']].to_sql('customers', engine, if_exists=if_exists, index=False)

    # Products
    products = df[['Product', 'Category', 'Unit Price']].drop_duplicates().rename(columns={'Product': 'product_name', 'Unit Price': 'unit_price', 'Category': 'category'})
    products.to_sql('products', engine, if_exists=if_exists, index=False)

    # Orders
    orders = df[['Order ID', 'Order Date', 'Customer ID', 'Payment Method']].drop_duplicates()
    orders = orders.rename(columns={'Order ID': 'order_id', 'Order Date': 'order_date', 'Customer ID': 'customer_id', 'Payment Method': 'payment_method'})
    orders.to_sql('orders', engine, if_exists=if_exists, index=False)

    # Order items: need product_id by joining product_name -> product_id; here we write best-effort with product_name
    order_items = df[['Order ID', 'Product', 'Quantity', 'Unit Price', 'Discount', 'Sales', 'Profit']].rename(columns={'Order ID': 'order_id', 'Product': 'product_name', 'Quantity': 'quantity', 'Unit Price': 'unit_price', 'Discount': 'discount', 'Sales': 'sales', 'Profit': 'profit'})
    order_items.to_sql('order_items', engine, if_exists=if_exists, index=False)

    log.info('Loaded flat data into database (tables: regions, customers, products, orders, order_items).')


def clean_pipeline(input_path: str, output_path: str, load_db: bool = False) -> pd.DataFrame:
    """End-to-end cleaning pipeline: read -> clean -> engineer -> save -> optional DB load."""
    df = read_csv(input_path)
    df = remove_duplicates(df)
    df = convert_types(df)
    report_missing(df)
    df = handle_missing_values(df)
    df = engineer_features(df)

    # Detect outliers on Sales and Profit for reporting
    for col in ['Sales', 'Profit']:
        if col in df.columns:
            try:
                mask, low, high = detect_outliers_iqr(df, col)
            except Exception:
                continue

    save_cleaned(df, output_path)

    if load_db:
        engine = create_db_engine_from_env()
        load_flat_to_db(df, engine)

    return df


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Clean raw sales CSV and optionally load to MySQL')
    parser.add_argument('--input', required=True, help='Path to raw CSV')
    parser.add_argument('--out', default='data/cleaned_sales.csv', help='Output cleaned CSV path')
    parser.add_argument('--load-db', action='store_true', help='Load cleaned data into MySQL using environment variables')
    args = parser.parse_args()

    df = clean_pipeline(args.input, args.out, args.load_db)
    log.info('Cleaning pipeline completed')

