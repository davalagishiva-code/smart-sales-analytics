from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def list_to_dict(values: List[Dict[str, Any]], key_name: str) -> Dict[str, Any]:
    return {item.get(key_name): item for item in values if item.get(key_name) is not None}


def filter_sales(sales: List[Dict[str, Any]], start_date: Optional[str] = None, end_date: Optional[str] = None,
                 category: Optional[str] = None, region: Optional[str] = None,
                 payment_method: Optional[str] = None) -> List[Dict[str, Any]]:
    filtered = []
    for sale in sales:
        sale_date = sale.get("date")
        if start_date and sale_date and sale_date < start_date:
            continue
        if end_date and sale_date and sale_date > end_date:
            continue
        if category and sale.get("category") != category:
            continue
        if region and sale.get("region") != region:
            continue
        if payment_method and sale.get("payment_method") != payment_method:
            continue
        filtered.append(sale)
    return filtered


def calculate_summary(sales: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not sales:
        return {
            "total_revenue": 0,
            "total_orders": 0,
            "total_profit": 0,
            "units_sold": 0,
            "average_order_value": 0,
            "profit_margin": 0,
            "total_sales": 0,
            "sales_count": 0,
        }

    total_revenue = sum(safe_float(sale.get("total_amount")) for sale in sales)
    total_profit = sum(
        safe_float(sale.get("total_amount")) - (safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity")))
        for sale in sales
    )
    total_orders = len(sales)
    units_sold = sum(int(sale.get("quantity", 0) or 0) for sale in sales)
    average_order_value = total_revenue / total_orders if total_orders else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_profit": round(total_profit, 2),
        "units_sold": units_sold,
        "average_order_value": round(average_order_value, 2),
        "profit_margin": round(profit_margin, 2),
        "total_sales": total_orders,
        "sales_count": total_orders,
    }


def sales_by_month(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, float] = defaultdict(float)
    for sale in sales:
        month = sale.get("date", "")[:7]
        if month:
            grouped[month] += safe_float(sale.get("total_amount"))
    return [{"month": month, "total": round(amount, 2)} for month, amount in sorted(grouped.items())]


def profit_by_month(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, float] = defaultdict(float)
    for sale in sales:
        month = sale.get("date", "")[:7]
        if month:
            revenue = safe_float(sale.get("total_amount"))
            cost = safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))
            grouped[month] += revenue - cost
    return [{"month": month, "profit": round(amount, 2)} for month, amount in sorted(grouped.items())]


def sales_by_category(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, float] = defaultdict(float)
    for sale in sales:
        category = sale.get("category") or "Unknown"
        grouped[category] += safe_float(sale.get("total_amount"))
    return [{"category": category, "total": round(amount, 2)} for category, amount in sorted(grouped.items(), key=lambda item: item[1], reverse=True)]


def profit_by_category(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, float] = defaultdict(float)
    for sale in sales:
        category = sale.get("category") or "Unknown"
        revenue = safe_float(sale.get("total_amount"))
        cost = safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))
        grouped[category] += revenue - cost
    return [{"category": category, "profit": round(amount, 2)} for category, amount in sorted(grouped.items(), key=lambda item: item[1], reverse=True)]


def sales_by_region(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, float] = defaultdict(float)
    for sale in sales:
        region = sale.get("region") or "Unknown"
        grouped[region] += safe_float(sale.get("total_amount"))
    return [{"region": region, "total": round(amount, 2)} for region, amount in sorted(grouped.items(), key=lambda item: item[1], reverse=True)]


def top_products(sales: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"product": "", "revenue": 0.0, "quantity": 0, "orders": 0})
    for sale in sales:
        product = sale.get("product") or "Unknown"
        entry = grouped[product]
        entry["product"] = product
        entry["revenue"] += safe_float(sale.get("total_amount"))
        entry["quantity"] += int(sale.get("quantity", 0) or 0)
        entry["orders"] += 1
    result = [
        {"product": entry["product"], "revenue": round(entry["revenue"], 2), "quantity": entry["quantity"], "orders": entry["orders"]}
        for entry in grouped.values()
    ]
    return sorted(result, key=lambda item: item["revenue"], reverse=True)[:limit]


def customer_behavior(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"customer": "", "orders": 0, "total_spending": 0.0})
    for sale in sales:
        customer = sale.get("customer") or "Unknown"
        entry = grouped[customer]
        entry["customer"] = customer
        entry["orders"] += 1
        entry["total_spending"] += float(sale.get("total_amount", 0) or 0)
    result = [
        {"customer": entry["customer"], "orders": entry["orders"], "total_spending": round(entry["total_spending"], 2)}
        for entry in grouped.values()
    ]
    return sorted(result, key=lambda item: item["total_spending"], reverse=True)


def profit_margin_by_category(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped_revenue: Dict[str, float] = defaultdict(float)
    grouped_profit: Dict[str, float] = defaultdict(float)
    for sale in sales:
        category = sale.get("category") or "Unknown"
        revenue = safe_float(sale.get("total_amount"))
        cost = safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))
        grouped_revenue[category] += revenue
        grouped_profit[category] += revenue - cost

    result = []
    for category, revenue in grouped_revenue.items():
        profit = grouped_profit.get(category, 0.0)
        margin = (profit / revenue * 100) if revenue else 0.0
        result.append({"category": category, "margin": round(margin, 2), "profit": round(profit, 2), "revenue": round(revenue, 2)})
    return sorted(result, key=lambda item: item["margin"], reverse=True)


def sales_vs_profit(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    grouped: Dict[str, Dict[str, float]] = defaultdict(lambda: {"sales": 0.0, "profit": 0.0})
    for sale in sales:
        key = sale.get("product") or sale.get("category") or "Unknown"
        revenue = safe_float(sale.get("total_amount"))
        cost = safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))
        grouped[key]["sales"] += revenue
        grouped[key]["profit"] += revenue - cost

    for key, values in grouped.items():
        profit_margin = (values["profit"] / values["sales"] * 100) if values["sales"] else 0.0
        result.append({
            "label": key,
            "sales": round(values["sales"], 2),
            "profit": round(values["profit"], 2),
            "profit_margin": round(profit_margin, 2),
        })
    return sorted(result, key=lambda item: item["sales"], reverse=True)


def previous_period_comparison(sales: List[Dict[str, Any]], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    start_date = filters.get("start_date") if filters else None
    end_date = filters.get("end_date") if filters else None
    if not start_date or not end_date:
        return {
            "current": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
            "previous": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
            "change": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
        }

    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        return {
            "current": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
            "previous": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
            "change": {"revenue": 0, "orders": 0, "profit": 0, "units_sold": 0, "profit_margin": 0},
        }

    day_count = (end_dt - start_dt).days + 1
    prev_end = start_dt - datetime.timedelta(days=1)
    prev_start = prev_end - datetime.timedelta(days=day_count - 1)

    current = filter_sales(sales, start_date=start_date, end_date=end_date)
    previous = filter_sales(sales, start_date=prev_start.isoformat(), end_date=prev_end.isoformat())
    current_summary = calculate_summary(current)
    previous_summary = calculate_summary(previous)

    def total_profit(items: List[Dict[str, Any]]) -> float:
        return sum(
            safe_float(item.get("total_amount")) - (safe_float(item.get("cost_price")) * safe_float(item.get("quantity")))
            for item in items
        )

    def total_revenue(items: List[Dict[str, Any]]) -> float:
        return sum(safe_float(item.get("total_amount")) for item in items)

    def pct_change(curr: float, prev: float) -> float:
        if prev == 0:
            return 0.0 if curr == 0 else 100.0
        return round(((curr - prev) / prev) * 100, 2)

    current_profit = total_profit(current)
    previous_profit = total_profit(previous)
    current_revenue = total_revenue(current)
    previous_revenue = total_revenue(previous)
    current_margin = (current_profit / current_revenue * 100) if current_revenue else 0.0
    previous_margin = (previous_profit / previous_revenue * 100) if previous_revenue else 0.0

    return {
        "current": {
            "revenue": round(current_summary["total_revenue"], 2),
            "orders": current_summary["total_orders"],
            "profit": round(current_profit, 2),
            "units_sold": current_summary["units_sold"],
            "profit_margin": round(current_margin, 2),
        },
        "previous": {
            "revenue": round(previous_summary["total_revenue"], 2),
            "orders": previous_summary["total_orders"],
            "profit": round(previous_profit, 2),
            "units_sold": previous_summary["units_sold"],
            "profit_margin": round(previous_margin, 2),
        },
        "change": {
            "revenue": pct_change(current_summary["total_revenue"], previous_summary["total_revenue"]),
            "orders": pct_change(current_summary["total_orders"], previous_summary["total_orders"]),
            "profit": pct_change(current_profit, previous_profit),
            "units_sold": pct_change(current_summary["units_sold"], previous_summary["units_sold"]),
            "profit_margin": pct_change(current_margin, previous_margin),
        },
    }


def build_business_insights(sales: List[Dict[str, Any]]) -> List[str]:
    if not sales:
        return ["No sales data available for the selected period."]

    category_totals = defaultdict(float)
    region_totals = defaultdict(float)
    product_totals = defaultdict(float)
    product_profit_margin = defaultdict(float)
    profit_by_product = defaultdict(float)

    for sale in sales:
        revenue = safe_float(sale.get("total_amount"))
        cost = safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))
        category_totals[sale.get("category") or "Unknown"] += revenue
        region_totals[sale.get("region") or "Unknown"] += revenue
        product_totals[sale.get("product") or "Unknown"] += revenue
        profit_by_product[sale.get("product") or "Unknown"] += revenue - cost

    top_category = max(category_totals.items(), key=lambda item: item[1])[0] if category_totals else "N/A"
    top_region = max(region_totals.items(), key=lambda item: item[1])[0] if region_totals else "N/A"
    top_product = max(product_totals.items(), key=lambda item: item[1])[0] if product_totals else "N/A"

    for product, revenue in product_totals.items():
        profit = profit_by_product.get(product, 0.0)
        product_profit_margin[product] = (profit / revenue * 100) if revenue else 0.0

    low_margin_product = min(product_profit_margin.items(), key=lambda item: item[1])[0] if product_profit_margin else "N/A"
    high_margin_category = max(
        [
            (category, (sum(safe_float(sale.get("total_amount")) - (safe_float(sale.get("cost_price")) * safe_float(sale.get("quantity"))) for sale in sales if sale.get("category") == category) / sum(safe_float(sale.get("total_amount")) for sale in sales if sale.get("category") == category) * 100) if sum(safe_float(sale.get("total_amount")) for sale in sales if sale.get("category") == category) else 0.0)
            for category in set(sale.get("category") for sale in sales)
        ],
        key=lambda item: item[1],
    )[0] if {sale.get("category") for sale in sales} else "N/A"

    total_revenue = sum(safe_float(sale.get("total_amount")) for sale in sales)
    avg_revenue = total_revenue / max(len(sales), 1)
    current_period = calculate_summary(sales)
    insights = [
        f"{top_category} generated the highest revenue in the selected period.",
        f"{top_region} led sales volume with the strongest regional performance.",
        f"{top_product} contributed the largest share of product revenue.",
        f"{low_margin_product} has a comparatively lower profit margin and may need pricing review.",
        f"{high_margin_category} is the strongest category by profit margin.",
    ]

    if current_period["total_profit"] > 0:
        insights.append("Profit remains positive across the selected period, indicating healthy contribution margins.")

    return insights[:5]


def generate_analysis_payload(sales: List[Dict[str, Any]], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    filtered = filter_sales(sales, **(filters or {}))
    summary = calculate_summary(filtered)
    monthly = sales_by_month(filtered)
    monthly_profit = profit_by_month(filtered)
    category_sales = sales_by_category(filtered)
    region_sales = sales_by_region(filtered)
    product_list = top_products(filtered, limit=10)
    profit_margin = profit_margin_by_category(filtered)
    scatter = sales_vs_profit(filtered)
    comparison = previous_period_comparison(filtered, filters or {})
    insights = build_business_insights(filtered)

    return {
        "summary": summary,
        "sales_by_month": monthly,
        "profit_by_month": monthly_profit,
        "sales_by_category": category_sales,
        "sales_by_region": region_sales,
        "top_products": product_list,
        "profit_margin_by_category": profit_margin,
        "sales_vs_profit": scatter,
        "performance_comparison": comparison,
        "business_insights": insights,
        "customer_behavior": customer_behavior(filtered),
        "revenue_trends": monthly,
        "best_worst_performers": {
            "top_revenue_category": max(category_sales, key=lambda item: item["total"], default={"category": "N/A", "total": 0}),
            "top_profit_category": max(profit_by_category(filtered), key=lambda item: item["profit"], default={"category": "N/A", "profit": 0}),
            "top_revenue_product": max(product_list, key=lambda item: item["revenue"], default={"product": "N/A", "revenue": 0}),
            "top_profit_product": max(
                [
                    {"product": item["product"], "profit": item["revenue"] * 0.35} for item in product_list
                ],
                key=lambda item: item["profit"],
                default={"product": "N/A", "profit": 0},
            ),
            "highest_profit_margin_category": max(profit_margin, key=lambda item: item["margin"], default={"category": "N/A", "margin": 0}),
            "highest_sales_region": max(region_sales, key=lambda item: item["total"], default={"region": "N/A", "total": 0}),
        },
    }


def build_report_rows(sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": sale.get("id"),
            "date": sale.get("date"),
            "product": sale.get("product"),
            "category": sale.get("category"),
            "quantity": sale.get("quantity"),
            "unit_price": sale.get("unit_price"),
            "discount": sale.get("discount"),
            "customer": sale.get("customer"),
            "region": sale.get("region"),
            "payment_method": sale.get("payment_method"),
            "total_amount": sale.get("total_amount"),
        }
        for sale in sales
    ]
