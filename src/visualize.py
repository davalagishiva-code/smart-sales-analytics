"""Visualization helpers using Matplotlib and Seaborn.
Saves charts to the `static/images/` directory for use in the Flask app.
"""
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set(style='whitegrid')


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_monthly_sales(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    df2 = df.copy()
    df2['YearMonth'] = pd.to_datetime(df2['Order Date']).dt.to_period('M').astype(str)
    agg = df2.groupby('YearMonth').agg(sales=('Sales', 'sum')).reset_index()
    plt.figure(figsize=(10,5))
    sns.lineplot(data=agg, x='YearMonth', y='sales', marker='o')
    plt.xticks(rotation=45)
    plt.title('Monthly Sales Trend')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_monthly_profit(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    df2 = df.copy()
    df2['YearMonth'] = pd.to_datetime(df2['Order Date']).dt.to_period('M').astype(str)
    agg = df2.groupby('YearMonth').agg(profit=('Profit', 'sum')).reset_index()
    plt.figure(figsize=(10,5))
    sns.lineplot(data=agg, x='YearMonth', y='profit', marker='o', color='green')
    plt.xticks(rotation=45)
    plt.title('Monthly Profit Trend')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_sales_by_category(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    agg = df.groupby('Category').agg(sales=('Sales', 'sum')).reset_index().sort_values('sales', ascending=False)
    plt.figure(figsize=(8,5))
    sns.barplot(data=agg, x='sales', y='Category', palette='Blues_d')
    plt.title('Sales by Category')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_sales_by_region(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    agg = df.groupby('Region').agg(sales=('Sales', 'sum')).reset_index().sort_values('sales', ascending=False)
    plt.figure(figsize=(8,5))
    sns.barplot(data=agg, x='sales', y='Region', palette='Greens_d')
    plt.title('Sales by Region')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_top_products(df: pd.DataFrame, out_path: str, n: int = 10):
    ensure_dir(os.path.dirname(out_path))
    agg = df.groupby('Product').agg(sales=('Sales', 'sum')).reset_index().sort_values('sales', ascending=False).head(n)
    plt.figure(figsize=(10,6))
    sns.barplot(data=agg, x='sales', y='Product', palette='Oranges_d')
    plt.title(f'Top {n} Products by Sales')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_profit_vs_sales(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    agg = df.groupby('Product').agg(sales=('Sales', 'sum'), profit=('Profit', 'sum')).reset_index()
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=agg, x='sales', y='profit')
    plt.title('Profit vs Sales (Product level)')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_customer_analysis(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    cust = df.groupby('Customer ID').agg(total_spent=('Sales', 'sum')).reset_index().sort_values('total_spent', ascending=False).head(20)
    plt.figure(figsize=(10,6))
    sns.barplot(data=cust, x='total_spent', y='Customer ID', palette='Purples_d')
    plt.title('Top 20 Customers by Spend')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
