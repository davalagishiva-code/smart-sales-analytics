"""Train the sales prediction model using cleaned data."""
import argparse
import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import pandas as pd
from src.ml_model import train_and_evaluate


def main(input_path: str, model_path: str):
    df = pd.read_csv(input_path, parse_dates=['Order Date'])
    metrics = train_and_evaluate(df, model_path)
    print('Training complete. Metrics:')
    print(metrics)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/cleaned_sales.csv')
    parser.add_argument('--model', default='models/sales_model.pkl')
    args = parser.parse_args()
    main(args.input, args.model)
