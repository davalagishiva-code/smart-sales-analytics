from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import json
import datetime
from typing import Any
import pandas as pd
from src.analysis import (
    compute_basic_metrics,
    monthly_aggregates,
    category_performance,
    top_products,
    customer_behavior,
    sales_by_region,
)
from src.db import initialize_database, insert_sale, fetch_sales, delete_sale, load_sales_dataframe, get_sales_categories
from src.ml_model import load_model, predict_from_dict
from src.refresh import regenerate_analytics


def load_model_metrics():
    metrics_path = os.path.join('models', 'sales_model.pkl.metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def format_inr(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return '₹0.00'

    negative = amount < 0
    amount = abs(amount)
    integer_part = int(amount)
    fraction = int(round((amount - integer_part) * 100))
    integer_str = str(integer_part)

    if len(integer_str) > 3:
        head = integer_str[:-3]
        tail = integer_str[-3:]
        head_parts = []
        while head:
            head_parts.append(head[-2:])
            head = head[:-2]
        integer_str = ','.join(reversed(head_parts)) + ',' + tail

    formatted = f"₹{integer_str}.{fraction:02d}"
    return f"-{formatted}" if negative else formatted


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.jinja_env.filters['format_inr'] = format_inr

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.datetime.now().year}

    @app.route('/')
    def dashboard():
        metrics_path = os.path.join('data', 'analysis', 'metrics.json')
        metrics = {}
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)

        model_metrics = load_model_metrics()
        images = []
        images_dir = os.path.join(app.static_folder, 'images')
        if os.path.exists(images_dir):
            images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        return render_template(
            'dashboard.html',
            page='dashboard',
            page_title='Dashboard',
            metrics=metrics,
            model_metrics=model_metrics,
            images=images,
        )

    initialize_database()
    regenerate_analytics()

    @app.route('/analysis')
    def analysis():
        df = load_sales_dataframe()

        categories = sorted(df['Category'].dropna().unique().tolist()) if not df.empty else []
        regions = sorted(df['Region'].dropna().unique().tolist()) if not df.empty else []
        payments = sorted(df['Payment Method'].dropna().unique().tolist()) if not df.empty else []

        start_date = request.args.get('start_date', df['Order Date'].min().strftime('%Y-%m-%d') if not df.empty else '')
        end_date = request.args.get('end_date', df['Order Date'].max().strftime('%Y-%m-%d') if not df.empty else '')
        selected_category = request.args.get('category', 'All')
        selected_region = request.args.get('region', 'All')
        selected_payment = request.args.get('payment_method', 'All')

        filtered = df.copy()
        if not filtered.empty:
            if start_date:
                filtered = filtered[filtered['Order Date'] >= pd.to_datetime(start_date)]
            if end_date:
                filtered = filtered[filtered['Order Date'] <= pd.to_datetime(end_date)]
            if selected_category != 'All':
                filtered = filtered[filtered['Category'] == selected_category]
            if selected_region != 'All':
                filtered = filtered[filtered['Region'] == selected_region]
            if selected_payment != 'All':
                filtered = filtered[filtered['Payment Method'] == selected_payment]

        metrics = compute_basic_metrics(filtered) if not filtered.empty else {}
        monthly = monthly_aggregates(filtered).to_dict(orient='records') if not filtered.empty else []
        category_data = category_performance(filtered).to_dict(orient='records') if not filtered.empty else []
        top_products_data = top_products(filtered, n=8).to_dict(orient='records') if not filtered.empty else []
        region_data = sales_by_region(filtered).to_dict(orient='records') if not filtered.empty else []

        analysis_files = []
        out_dir = os.path.join('data', 'analysis')
        if os.path.exists(out_dir):
            analysis_files = [f for f in os.listdir(out_dir) if f.lower().endswith(('.csv', '.json'))]

        images = []
        images_dir = os.path.join(app.static_folder, 'images')
        if os.path.exists(images_dir):
            images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        return render_template(
            'analysis.html',
            page='analysis',
            page_title='Sales Analysis',
            filters={
                'start_date': start_date,
                'end_date': end_date,
                'category': selected_category,
                'region': selected_region,
                'payment_method': selected_payment,
            },
            categories=categories,
            regions=regions,
            payments=payments,
            metrics=metrics,
            monthly=monthly,
            category_data=category_data,
            top_products_data=top_products_data,
            region_data=region_data,
            analysis_files=analysis_files,
            images=images,
        )

    @app.route('/analysis/download/<path:filename>')
    def analysis_download(filename):
        return send_from_directory(os.path.join('data', 'analysis'), filename, as_attachment=True)

    @app.route('/products')
    def products():
        df = load_sales_dataframe()
        product_rows = top_products(df, n=15).to_dict(orient='records') if not df.empty else []
        category_data = category_performance(df).to_dict(orient='records') if not df.empty else []
        product_summary = {
            'total_products': int(df['Product'].nunique()) if not df.empty else 0,
            'total_revenue': round(float(df['Sales'].sum()), 2) if not df.empty else 0,
            'total_profit': round(float(df['Profit'].sum()), 2) if not df.empty else 0,
        }
        return render_template(
            'products.html',
            page='products',
            page_title='Products',
            products=product_rows,
            category_data=category_data,
            product_summary=product_summary,
        )

    @app.route('/customers')
    def customers():
        df = load_sales_dataframe()
        customer_rows = customer_behavior(df, n=15).to_dict(orient='records') if not df.empty else []
        customer_summary = {
            'customer_count': int(df['Customer ID'].nunique()) if not df.empty else 0,
            'total_orders': int(df['Order ID'].nunique()) if not df.empty else 0,
            'average_order_value': round(float(df['Sales'].sum()) / int(df['Order ID'].nunique()), 2) if not df.empty and int(df['Order ID'].nunique()) else 0,
        }
        return render_template(
            'customers.html',
            page='customers',
            page_title='Customers',
            customers=customer_rows,
            customer_summary=customer_summary,
        )

    @app.route('/reports')
    def reports():
        images = []
        images_dir = os.path.join(app.static_folder, 'images')
        if os.path.exists(images_dir):
            images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        analysis_files = []
        out_dir = os.path.join('data', 'analysis')
        if os.path.exists(out_dir):
            analysis_files = [f for f in os.listdir(out_dir) if f.lower().endswith(('.csv', '.json'))]

        return render_template(
            'reports.html',
            page='reports',
            page_title='Reports',
            images=images,
            analysis_files=analysis_files,
        )

    @app.route('/settings')
    def settings():
        return render_template('settings.html', page='settings', page_title='Settings')

    @app.route('/add-sale', methods=['GET', 'POST'])
    def add_sale():
        error = None
        success = None
        categories = ['Mobile', 'Laptop', 'Tablet', 'Accessories', 'Other']
        payments = ['Cash', 'UPI', 'Card', 'Other']
        sale = {
            'product': '',
            'category': 'Mobile',
            'customer_name': '',
            'quantity': 1,
            'cost_price': 0.0,
            'selling_price': 0.0,
            'discount': 0.0,
            'discount_amount': 0.0,
            'sale_date': datetime.date.today().strftime('%Y-%m-%d'),
            'payment_method': 'Cash',
        }

        if request.method == 'POST':
            try:
                sale['product'] = request.form.get('product', '').strip()
                sale['category'] = request.form.get('category', 'Other')
                sale['customer_name'] = request.form.get('customer_name', '').strip()
                sale['quantity'] = int(request.form.get('quantity', '0'))
                sale['cost_price'] = float(request.form.get('cost_price', '0'))
                sale['selling_price'] = float(request.form.get('selling_price', '0'))
                sale['discount'] = float(request.form.get('discount', '0'))
                sale['sale_date'] = request.form.get('sale_date', sale['sale_date'])
                sale['payment_method'] = request.form.get('payment_method', 'Cash')
                sale['region'] = request.form.get('region', 'Other')

                if not sale['product']:
                    raise ValueError('Product Name is required.')
                if not sale['customer_name']:
                    raise ValueError('Customer Name is required.')
                if sale['quantity'] <= 0:
                    raise ValueError('Quantity must be greater than zero.')
                if sale['cost_price'] < 0:
                    raise ValueError('Cost Price cannot be negative.')
                if sale['selling_price'] < 0:
                    raise ValueError('Selling Price cannot be negative.')
                if sale['discount'] < 0:
                    raise ValueError('Discount cannot be negative.')
                if sale['discount'] > 100:
                    raise ValueError('Discount cannot exceed 100%.')
                if not sale['sale_date']:
                    raise ValueError('Sale Date is required.')

                gross_sales = round(sale['quantity'] * sale['selling_price'], 2)
                sale['discount_amount'] = round(gross_sales * (sale['discount'] / 100), 2)
                final_sales = round(gross_sales - sale['discount_amount'], 2)
                sale['total_sales'] = final_sales
                sale['total_cost'] = round(sale['quantity'] * sale['cost_price'], 2)
                sale['profit'] = round(final_sales - sale['total_cost'], 2)
                db_sale = sale.copy()
                db_sale['discount'] = round(sale['discount'] / 100, 4)

                insert_sale(db_sale)
                regenerate_analytics()
                return redirect(url_for('add_sale', success='1'))
            except Exception as e:
                error = str(e)

        if request.method == 'GET' and request.args.get('success') == '1':
            success = 'Sale added successfully and analytics refreshed.'

        return render_template(
            'add_sale.html',
            page='add_sale',
            page_title='Add Sale',
            categories=categories,
            payments=payments,
            sale=sale,
            error=error,
            success=success,
        )

    @app.route('/sales-history')
    def sales_history():
        search = request.args.get('search', '').strip()
        category = request.args.get('category', 'All')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        sort_by = request.args.get('sort_by', 'sale_date')
        sort_dir = request.args.get('sort_dir', 'desc')

        rows = fetch_sales(search=search, category=category, start_date=start_date, end_date=end_date, sort_by=sort_by, sort_dir=sort_dir)
        categories = ['All'] + get_sales_categories()

        return render_template(
            'sales_history.html',
            page='sales_history',
            page_title='Sales History',
            sales=rows,
            categories=categories,
            filters={
                'search': search,
                'category': category,
                'start_date': start_date,
                'end_date': end_date,
                'sort_by': sort_by,
                'sort_dir': sort_dir,
            },
        )

    @app.route('/sales-history/delete/<int:sale_id>', methods=['POST'])
    def sales_history_delete(sale_id):
        delete_sale(sale_id)
        regenerate_analytics()
        return jsonify({'deleted': True})

    @app.route('/predict', methods=['GET', 'POST'])
    def predict():
        result = None
        error = None
        prediction_input = {}
        if request.method == 'POST':
            try:
                prediction_input = {
                    'Quantity': float(request.form.get('quantity', 1)),
                    'Unit Price': float(request.form.get('unit_price', 0)),
                    'Discount': float(request.form.get('discount', 0)),
                    'Category': request.form.get('category', 'Unknown'),
                    'Region': request.form.get('region', 'Unknown'),
                    'Payment Method': request.form.get('payment_method', 'Unknown'),
                }
                model = load_model()
                pred = predict_from_dict(model, prediction_input)
                result = round(pred, 2)
            except Exception as e:
                error = str(e)

        categories = ['Electronics', 'Furniture', 'Groceries', 'Stationery', 'Accessories', 'Gift']
        regions = ['North', 'South', 'East', 'West', 'Central']
        payments = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']
        model_metrics = load_model_metrics()

        return render_template(
            'predict.html',
            page='predict',
            page_title='Prediction',
            result=result,
            error=error,
            prediction_input=prediction_input,
            categories=categories,
            regions=regions,
            payments=payments,
            model_metrics=model_metrics,
        )

    @app.route('/api/predict', methods=['POST'])
    def api_predict():
        payload = request.get_json() or {}
        try:
            model = load_model()
            pred = predict_from_dict(model, payload)
            return jsonify({'prediction': pred})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/about')
    def about():
        return render_template('about.html', page='about', page_title='About')

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
