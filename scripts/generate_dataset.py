"""Generate a realistic sales dataset (CSV) for Smart Sales Analytics.

Usage:
    python scripts/generate_dataset.py --rows 1000 --out data/raw_sales.csv

This script creates columns:
Order ID,Order Date,Customer ID,Customer Name,Product,Category,Region,Quantity,Unit Price,Discount,Sales,Profit,Payment Method
"""
import csv
import random
import argparse
from datetime import datetime, timedelta

PRODUCTS = [
    ("UltraPhone X", "Electronics", 699.0),
    ("PowerBank 20K", "Electronics", 49.0),
    ("Ergo Chair", "Furniture", 199.0),
    ("Standing Desk", "Furniture", 399.0),
    ("Office Lamp", "Furniture", 29.0),
    ("Coffee Beans 1kg", "Groceries", 15.0),
    ("Notebook A4", "Stationery", 3.5),
    ("Pen Set", "Stationery", 5.0),
    ("NoiseCancel Headset", "Electronics", 129.0),
    ("Fitness Band", "Electronics", 59.0),
    ("Water Bottle", "Accessories", 12.0),
    ("Backpack", "Accessories", 49.0),
    ("SmartWatch Pro", "Electronics", 249.0),
    ("Desk Organizer", "Furniture", 18.0),
    ("Gift Card $50", "Gift", 50.0),
]

CUSTOMERS = [
    "Alice Johnson", "Bob Smith", "Carol Lee", "David Brown", "Eva Green",
    "Frank Wright", "Grace Kim", "Hector Cruz", "Ivy Patel", "Jack Liu",
    "Kumar Singh", "Lara Becker", "Mona Rao", "Nina Gomez", "Omar Ali"
]

REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Bank Transfer", "Cash"]
DISCOUNTS = [0.0, 0.05, 0.1, 0.15]

def random_date(start, end):
    delta = end - start
    days = random.randrange(delta.days + 1)
    return start + timedelta(days=days)

def generate_row(i, start_date, end_date):
    order_id = f"ORD{i:06d}"
    order_date = random_date(start_date, end_date).strftime('%Y-%m-%d')
    cust_idx = random.randrange(len(CUSTOMERS))
    customer_id = f"CUST{cust_idx+1:04d}"
    customer_name = CUSTOMERS[cust_idx]
    product, category, unit_price = random.choice(PRODUCTS)
    region = random.choice(REGIONS)
    quantity = random.randint(1, 10)
    discount = random.choice(DISCOUNTS)
    sales = round(quantity * unit_price * (1 - discount), 2)
    # set profit margin by category
    base_margin = {
        'Electronics': 0.18,
        'Furniture': 0.22,
        'Groceries': 0.12,
        'Stationery': 0.25,
        'Accessories': 0.2,
        'Gift': 0.15
    }
    margin = base_margin.get(category, 0.18) * random.uniform(0.9, 1.1)
    profit = round(sales * margin, 2)
    payment = random.choice(PAYMENT_METHODS)
    return [order_id, order_date, customer_id, customer_name, product, category, region,
            quantity, unit_price, discount, sales, profit, payment]

def generate_csv(rows, out_path):
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    header = ['Order ID','Order Date','Customer ID','Customer Name','Product','Category','Region',
              'Quantity','Unit Price','Discount','Sales','Profit','Payment Method']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(1, rows+1):
            writer.writerow(generate_row(i, start_date, end_date))
    print(f"Generated {rows} rows -> {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=1000, help='Number of rows to generate')
    parser.add_argument('--out', type=str, default='data/raw_sales.csv', help='Output CSV path')
    args = parser.parse_args()
    generate_csv(args.rows, args.out)

if __name__ == '__main__':
    main()
