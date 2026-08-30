"""Load the trained model and run a sample prediction."""
import argparse
import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from src.ml_model import load_model, predict_from_dict


def main(model_path: str):
    model = load_model(model_path)
    sample = {
        'Quantity': 2,
        'Unit Price': 49.0,
        'Discount': 0.05,
        'Category': 'Electronics',
        'Region': 'North',
        'Payment Method': 'Credit Card'
    }
    pred = predict_from_dict(model, sample)
    print('Sample input:', sample)
    print(f'Predicted Sales: {pred:.2f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='models/sales_model.pkl')
    args = parser.parse_args()
    main(args.model)
