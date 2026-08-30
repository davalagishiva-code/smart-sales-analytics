"""Generate charts from cleaned sales CSV and save to static/images."""
import argparse
import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import pandas as pd
from src.visualize import plot_monthly_sales, plot_monthly_profit, plot_sales_by_category, plot_sales_by_region, plot_top_products, plot_profit_vs_sales, plot_customer_analysis


def main(input_path: str, out_dir: str):
    df = pd.read_csv(input_path, parse_dates=['Order Date'])
    os.makedirs(out_dir, exist_ok=True)
    plot_monthly_sales(df, os.path.join(out_dir, 'monthly_sales.png'))
    plot_monthly_profit(df, os.path.join(out_dir, 'monthly_profit.png'))
    plot_sales_by_category(df, os.path.join(out_dir, 'sales_by_category.png'))
    plot_sales_by_region(df, os.path.join(out_dir, 'sales_by_region.png'))
    plot_top_products(df, os.path.join(out_dir, 'top_products.png'))
    plot_profit_vs_sales(df, os.path.join(out_dir, 'profit_vs_sales.png'))
    plot_customer_analysis(df, os.path.join(out_dir, 'top_customers.png'))
    print(f'Charts saved to {out_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/cleaned_sales.csv')
    parser.add_argument('--out', default='static/images')
    args = parser.parse_args()
    main(args.input, args.out)
