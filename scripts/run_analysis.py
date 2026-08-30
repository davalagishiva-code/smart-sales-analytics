"""Run analysis on cleaned sales CSV and save summary outputs.

Usage:
    python scripts/run_analysis.py --input data/cleaned_sales.csv --out data/analysis
"""
import argparse
import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from src.analysis import load_cleaned, compute_basic_metrics, top_products, most_profitable_products, sales_by_region, monthly_aggregates, category_performance, customer_behavior, save_json, save_df


def main(input_path: str, out_dir: str):
    df = load_cleaned(input_path)
    metrics = compute_basic_metrics(df)
    os.makedirs(out_dir, exist_ok=True)
    save_json(metrics, os.path.join(out_dir, 'metrics.json'))

    save_df(top_products(df, 10), os.path.join(out_dir, 'top_products.csv'))
    save_df(most_profitable_products(df, 10), os.path.join(out_dir, 'most_profitable_products.csv'))
    save_df(sales_by_region(df), os.path.join(out_dir, 'sales_by_region.csv'))
    save_df(monthly_aggregates(df), os.path.join(out_dir, 'monthly_aggregates.csv'))
    save_df(category_performance(df), os.path.join(out_dir, 'category_performance.csv'))
    save_df(customer_behavior(df, 20), os.path.join(out_dir, 'top_customers.csv'))

    print(f'Analysis outputs written to {out_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/cleaned_sales.csv')
    parser.add_argument('--out', default='data/analysis')
    args = parser.parse_args()
    main(args.input, args.out)
