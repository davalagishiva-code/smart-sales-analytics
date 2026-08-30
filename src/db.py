import os
import sqlite3
from typing import Any, Dict, List, Optional

import pandas as pd

DB_PATH = os.path.join('data', 'sales_data.db')
DEFAULT_REGION = 'Other'


def get_db_path() -> str:
    return DB_PATH


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(csv_path: str = os.path.join('data', 'cleaned_sales.csv')) -> None:
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                total_sales REAL NOT NULL,
                total_cost REAL NOT NULL,
                profit REAL NOT NULL,
                discount REAL NOT NULL DEFAULT 0.0,
                payment_method TEXT NOT NULL,
                region TEXT NOT NULL DEFAULT 'Other',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor = conn.execute('PRAGMA table_info(sales)')
        columns = [row[1] for row in cursor.fetchall()]
        if 'discount' not in columns:
            conn.execute('ALTER TABLE sales ADD COLUMN discount REAL NOT NULL DEFAULT 0.0')

        cursor = conn.execute('SELECT COUNT(1) FROM sales')
        total_rows = cursor.fetchone()[0]
        if total_rows == 0 and os.path.exists(csv_path):
            _load_csv_into_db(csv_path, conn)


def _load_csv_into_db(csv_path: str, conn: sqlite3.Connection) -> None:
    df = pd.read_csv(csv_path, parse_dates=['Order Date'])
    insert_sql = '''
        INSERT INTO sales (
            sale_date, product, category, customer_name, quantity,
            cost_price, selling_price, total_sales, total_cost, profit,
            discount, payment_method, region
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    records = []
    for _, row in df.iterrows():
        quantity = int(row.get('Quantity', 0) or 0)
        selling_price = float(row.get('Unit Price', 0) or 0)
        profit = float(row.get('Profit', 0) or 0)
        total_sales = float(row.get('Sales', 0) or 0)
        discount_value = float(row.get('Discount', 0) or 0)
        if discount_value > 1:
            discount_value = discount_value / 100.0
        discount_value = max(0.0, min(discount_value, 1.0))
        cost_price = ((total_sales - profit) / quantity) if quantity else 0.0
        if quantity and cost_price < 0:
            cost_price = 0.0
        total_cost = round(cost_price * quantity, 2)
        records.append(
            (
                row['Order Date'].strftime('%Y-%m-%d') if not pd.isna(row['Order Date']) else '',
                row.get('Product', 'Unknown'),
                row.get('Category', 'Other'),
                row.get('Customer Name', 'Unknown'),
                quantity,
                round(cost_price, 2),
                round(selling_price, 2),
                round(total_sales, 2),
                round(total_cost, 2),
                round(profit, 2),
                round(discount_value, 4),
                row.get('Payment Method', 'Other'),
                row.get('Region', DEFAULT_REGION) or DEFAULT_REGION,
            )
        )

    conn.executemany(insert_sql, records)


def insert_sale(sale_data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    with conn:
        cursor = conn.execute(
            '''
            INSERT INTO sales (
                sale_date, product, category, customer_name, quantity,
                cost_price, selling_price, total_sales, total_cost, profit,
                discount, payment_method, region
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                sale_data['sale_date'],
                sale_data['product'],
                sale_data['category'],
                sale_data['customer_name'],
                sale_data['quantity'],
                sale_data['cost_price'],
                sale_data['selling_price'],
                sale_data['total_sales'],
                sale_data['total_cost'],
                sale_data['profit'],
                sale_data.get('discount', 0.0),
                sale_data['payment_method'],
                sale_data.get('region', DEFAULT_REGION),
            )
        )
        return cursor.lastrowid


def delete_sale(sale_id: int) -> None:
    conn = get_db_connection()
    with conn:
        conn.execute('DELETE FROM sales WHERE id = ?', (sale_id,))


def fetch_sales(
    search: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: str = 'sale_date',
    sort_dir: str = 'desc',
) -> List[Dict[str, Any]]:
    allowed_sort = {'sale_date', 'total_sales', 'profit', 'quantity'}
    if sort_by not in allowed_sort:
        sort_by = 'sale_date'
    sort_dir = 'asc' if str(sort_dir).lower() == 'asc' else 'desc'

    sql = 'SELECT * FROM sales WHERE 1=1'
    params: List[Any] = []

    if category and category != 'All':
        sql += ' AND category = ?'
        params.append(category)
    if start_date:
        sql += ' AND sale_date >= ?'
        params.append(start_date)
    if end_date:
        sql += ' AND sale_date <= ?'
        params.append(end_date)
    if search:
        like = f'%{search}%'
        sql += ' AND (product LIKE ? OR customer_name LIKE ? OR payment_method LIKE ?)'
        params.extend([like, like, like])

    sql += f' ORDER BY {sort_by} {sort_dir.upper()}'
    conn = get_db_connection()
    cursor = conn.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_sales_categories() -> List[str]:
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT category FROM sales ORDER BY category')
    categories = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return categories


def load_sales_dataframe() -> pd.DataFrame:
    conn = get_db_connection()
    try:
        df = pd.read_sql_query('SELECT * FROM sales ORDER BY sale_date', conn, parse_dates=['sale_date'])
    finally:
        conn.close()

    if df.empty:
        return df

    df['Order ID'] = df['id'].apply(lambda number: f'SALE{int(number):06d}')
    df['Order Date'] = pd.to_datetime(df['sale_date'])
    df['Customer ID'] = df['customer_name']
    df['Customer Name'] = df['customer_name']
    df['Product'] = df['product']
    df['Category'] = df['category']
    df['Region'] = df['region'].fillna(DEFAULT_REGION) if 'region' in df.columns else DEFAULT_REGION
    df['Quantity'] = df['quantity']
    df['Unit Price'] = df['selling_price']
    df['Discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0.0) if 'discount' in df.columns else 0.0
    df['Sales'] = df['total_sales']
    df['Profit'] = df['profit']
    df['Payment Method'] = df['payment_method']
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

    return df[
        [
            'Order ID', 'Order Date', 'Customer ID', 'Customer Name', 'Product',
            'Category', 'Region', 'Quantity', 'Unit Price', 'Discount',
            'Sales', 'Profit', 'Payment Method', 'Year', 'Month', 'YearMonth',
        ]
    ]
