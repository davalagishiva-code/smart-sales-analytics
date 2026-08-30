import os
from pathlib import Path

from src.analysis import (
    compute_basic_metrics,
    top_products,
    most_profitable_products,
    sales_by_region,
    monthly_aggregates,
    category_performance,
    customer_behavior,
    save_json,
    save_df,
)
from src.db import load_sales_dataframe
from src.visualize import (
    plot_monthly_sales,
    plot_monthly_profit,
    plot_sales_by_category,
    plot_sales_by_region,
    plot_top_products,
    plot_profit_vs_sales,
    plot_customer_analysis,
)


def regenerate_analytics() -> None:
    df = load_sales_dataframe()
    if df.empty:
        return

    out_dir = Path('data') / 'analysis'
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = compute_basic_metrics(df)
    save_json(metrics, str(out_dir / 'metrics.json'))
    save_df(top_products(df, 10), str(out_dir / 'top_products.csv'))
    save_df(most_profitable_products(df, 10), str(out_dir / 'most_profitable_products.csv'))
    save_df(sales_by_region(df), str(out_dir / 'sales_by_region.csv'))
    save_df(monthly_aggregates(df), str(out_dir / 'monthly_aggregates.csv'))
    save_df(category_performance(df), str(out_dir / 'category_performance.csv'))
    save_df(customer_behavior(df, 20), str(out_dir / 'top_customers.csv'))

    image_dir = Path('static') / 'images'
    image_dir.mkdir(parents=True, exist_ok=True)
    plot_monthly_sales(df, str(image_dir / 'monthly_sales.png'))
    plot_monthly_profit(df, str(image_dir / 'monthly_profit.png'))
    plot_sales_by_category(df, str(image_dir / 'sales_by_category.png'))
    plot_sales_by_region(df, str(image_dir / 'sales_by_region.png'))
    plot_top_products(df, str(image_dir / 'top_products.png'))
    plot_profit_vs_sales(df, str(image_dir / 'profit_vs_sales.png'))
    plot_customer_analysis(df, str(image_dir / 'top_customers.png'))
