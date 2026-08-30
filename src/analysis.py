"""Analysis utilities: aggregate calculations and summaries

Functions are small, testable, and return pandas DataFrames or Python dicts
that can be used by visualization scripts or the Flask app.
"""
from typing import Dict
import pandas as pd
import os
import json
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def load_cleaned(path: str) -> pd.DataFrame:
    """Load cleaned sales CSV produced by the cleaning pipeline."""
    df = pd.read_csv(path, parse_dates=['Order Date'])
    log.info(f"Loaded cleaned data: {len(df)} rows")
    return df


def compute_basic_metrics(df: pd.DataFrame) -> Dict[str, float]:
    total_sales = float(df['Sales'].sum())
    total_profit = float(df['Profit'].sum())
    total_orders = int(df['Order ID'].nunique()) if 'Order ID' in df.columns else int(df.shape[0])
    avg_order_value = total_sales / total_orders if total_orders else 0.0
    return {
        'total_sales': round(total_sales, 2),
        'total_profit': round(total_profit, 2),
        'total_orders': total_orders,
        'avg_order_value': round(avg_order_value, 2)
    }


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    m = df.groupby('Product').agg(total_qty=('Quantity', 'sum'), total_sales=('Sales', 'sum'), total_profit=('Profit', 'sum')).reset_index()
    m = m.sort_values('total_qty', ascending=False).head(n)
    return m


def most_profitable_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    m = df.groupby('Product').agg(total_profit=('Profit', 'sum'), total_sales=('Sales', 'sum')).reset_index()
    m = m.sort_values('total_profit', ascending=False).head(n)
    return m


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('Region').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).reset_index().sort_values('sales', ascending=False)


def monthly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    if 'Order Date' not in df2.columns:
        raise ValueError('Order Date column missing')
    df2['YearMonth'] = df2['Order Date'].dt.to_period('M').astype(str)
    return df2.groupby('YearMonth').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).reset_index().sort_values('YearMonth')


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('Category').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).reset_index().sort_values('sales', ascending=False)


def customer_behavior(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    m = df.groupby(['Customer ID', 'Customer Name']).agg(orders_count=('Order ID', 'nunique'), total_spent=('Sales', 'sum')).reset_index()
    return m.sort_values('total_spent', ascending=False).head(n)


def save_json(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
    log.info(f"Saved JSON to {path}")


def save_df(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    log.info(f"Saved CSV to {path}")


if __name__ == '__main__':
    print('Use scripts/run_analysis.py to run the analysis and save outputs')
