import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

def _ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(PRODUCTS_FILE):
        default_products = [
            {
                "id": 1,
                "code": "R-001",
                "name": "Ring 1 (Silver Floral)",
                "cost_price": 350.0,
                "selling_price": 650.0,
                "stock": 15,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 2,
                "code": "R-002",
                "name": "Ring 2 (Gold Minimalist)",
                "cost_price": 400.0,
                "selling_price": 750.0,
                "stock": 12,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 3,
                "code": "N-001",
                "name": "Butterfly Pendant Necklace",
                "cost_price": 550.0,
                "selling_price": 1100.0,
                "stock": 8,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 4,
                "code": "E-001",
                "name": "Pearl Drop Earrings",
                "cost_price": 250.0,
                "selling_price": 500.0,
                "stock": 20,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_products, f, indent=2, ensure_ascii=False)

    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)

def _read_json(filepath):
    _ensure_data_files()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_json(filepath, data):
    _ensure_data_files()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ----------------- Products Management -----------------

def get_all_products(search=None):
    products = _read_json(PRODUCTS_FILE)
    if search:
        q = search.strip().lower()
        products = [p for p in products if q in p.get("code", "").lower() or q in p.get("name", "").lower()]
    products.sort(key=lambda x: x.get("code", ""))
    return products

def get_product_by_id(product_id):
    products = _read_json(PRODUCTS_FILE)
    for p in products:
        if p.get("id") == int(product_id):
            return p
    return None

def get_product_by_code(code):
    products = _read_json(PRODUCTS_FILE)
    c = code.strip().upper()
    for p in products:
        if p.get("code", "").upper() == c:
            return p
    return None

def add_product(code, name, cost_price, selling_price, stock):
    clean_code = code.strip().upper()
    products = _read_json(PRODUCTS_FILE)
    if any(p.get("code", "").upper() == clean_code for p in products):
        return False, f"A product with code '{clean_code}' already exists."

    new_id = max([p.get("id", 0) for p in products], default=0) + 1
    new_prod = {
        "id": new_id,
        "code": clean_code,
        "name": name.strip(),
        "cost_price": float(cost_price),
        "selling_price": float(selling_price),
        "stock": int(stock),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    products.append(new_prod)
    _write_json(PRODUCTS_FILE, products)
    return True, f"Product {clean_code} added successfully."

def update_product(product_id, code, name, cost_price, selling_price, stock):
    clean_code = code.strip().upper()
    pid = int(product_id)
    products = _read_json(PRODUCTS_FILE)
    
    for p in products:
        if p.get("id") != pid and p.get("code", "").upper() == clean_code:
            return False, f"Code '{clean_code}' is already used by another product."

    for p in products:
        if p.get("id") == pid:
            p["code"] = clean_code
            p["name"] = name.strip()
            p["cost_price"] = float(cost_price)
            p["selling_price"] = float(selling_price)
            p["stock"] = int(stock)
            p["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _write_json(PRODUCTS_FILE, products)
            return True, f"Product {clean_code} updated successfully."
            
    return False, "Product not found."

def delete_product(product_id):
    pid = int(product_id)
    products = _read_json(PRODUCTS_FILE)
    initial_len = len(products)
    products = [p for p in products if p.get("id") != pid]
    if len(products) < initial_len:
        _write_json(PRODUCTS_FILE, products)
        return True, "Product deleted."
    return False, "Product not found."

# ----------------- Orders & Billing Management -----------------

def generate_invoice_no():
    """Generates sequential invoice number for today: INV-YYYYMMDD-001"""
    today_str = datetime.now().strftime("%Y%m%d")
    orders = _read_json(ORDERS_FILE)
    prefix = f"INV-{today_str}-"
    todays_orders = [o for o in orders if o.get("invoice_no", "").startswith(prefix)]
    seq = len(todays_orders) + 1
    return f"{prefix}{seq:03d}"

def create_order(store_name, customer_name, customer_address, customer_phone, payment_method, notes, items, bill_image_path, channel="Other", delivery_charge=0.0):
    orders = _read_json(ORDERS_FILE)
    products = _read_json(PRODUCTS_FILE)

    invoice_no = generate_invoice_no()

    total_cost = 0.0
    total_selling = 0.0
    processed_items = []
    prod_map = {p.get("code", "").upper(): p for p in products}

    for itm in items:
        code = itm["product_code"].strip().upper()
        qty = int(itm["quantity"])
        cp = float(itm["cost_price"])
        sp = float(itm["selling_price"])
        subtot = round(sp * qty, 2)
        name = itm.get("product_name", "").strip() or (prod_map.get(code, {}).get("name", code))

        total_cost += cp * qty
        total_selling += subtot

        processed_items.append({
            "product_code": code,
            "product_name": name,
            "quantity": qty,
            "cost_price": cp,
            "selling_price": sp,
            "subtotal": subtot
        })

        if code in prod_map:
            prod_map[code]["stock"] = max(0, prod_map[code]["stock"] - qty)

    total_profit = round(total_selling - total_cost, 2)
    delivery_charge = round(max(0.0, float(delivery_charge or 0)), 2)
    new_order_id = max([o.get("id", 0) for o in orders], default=0) + 1

    order_record = {
        "id": new_order_id,
        "invoice_no": invoice_no,
        "store_name": store_name,
        "channel": channel if channel in {"Instagram", "WhatsApp", "Other"} else "Other",
        "customer_name": customer_name.strip(),
        "customer_address": customer_address.strip(),
        "customer_phone": customer_phone.strip() if customer_phone else "",
        "payment_method": payment_method,
        "notes": notes.strip() if notes else "",
        "items": processed_items,
        "total_cost": round(total_cost, 2),
        "total_selling": round(total_selling, 2),
        "delivery_charge": delivery_charge,
        "grand_total": round(total_selling + delivery_charge, 2),
        "total_profit": total_profit,
        "bill_image_path": bill_image_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    orders.append(order_record)

    _write_json(ORDERS_FILE, orders)
    _write_json(PRODUCTS_FILE, products)

    return new_order_id, invoice_no

def get_order_by_id(order_id):
    oid = int(order_id)
    orders = _read_json(ORDERS_FILE)
    for o in orders:
        if o.get("id") == oid:
            return o
    return None

def get_all_orders(store_filter=None, date_filter=None, channel_filter=None):
    orders = _read_json(ORDERS_FILE)
    results = orders[:]
    if store_filter and store_filter.lower() != "all":
        results = [o for o in results if o.get("store_name", "").lower() == store_filter.lower()]

    if date_filter:
        results = [o for o in results if o.get("created_at", "").startswith(date_filter)]
    if channel_filter and channel_filter.lower() != "all":
        results = [o for o in results if o.get("channel", "Other").lower() == channel_filter.lower()]

    results.sort(key=lambda x: x.get("id", 0), reverse=True)
    return results

def delete_order(order_id):
    oid = int(order_id)
    orders = _read_json(ORDERS_FILE)
    products = _read_json(PRODUCTS_FILE)
    prod_map = {p.get("code", "").upper(): p for p in products}

    target_order = None
    for o in orders:
        if o.get("id") == oid:
            target_order = o
            break

    if not target_order:
        return False

    for item in target_order.get("items", []):
        code = item.get("product_code", "").upper()
        qty = int(item.get("quantity", 0))
        if code in prod_map:
            prod_map[code]["stock"] += qty

    orders = [o for o in orders if o.get("id") != oid]

    _write_json(ORDERS_FILE, orders)
    _write_json(PRODUCTS_FILE, products)
    return True

def get_dashboard_stats():
    products = _read_json(PRODUCTS_FILE)
    orders = _read_json(ORDERS_FILE)

    total_products = len(products)
    total_orders = len(orders)
    total_revenue = sum(float(o.get("total_selling", 0.0)) for o in orders)
    total_cost = sum(float(o.get("total_cost", 0.0)) for o in orders)
    total_profit = sum(float(o.get("total_profit", 0.0)) for o in orders)

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_orders_list = [o for o in orders if o.get("created_at", "").startswith(today_str)]
    today_orders = len(today_orders_list)
    today_revenue = sum(float(o.get("total_selling", 0.0)) for o in today_orders_list)
    today_profit = sum(float(o.get("total_profit", 0.0)) for o in today_orders_list)

    month_prefix = datetime.now().strftime("%Y-%m")
    month_orders_list = [o for o in orders if o.get("created_at", "").startswith(month_prefix)]
    month_orders = len(month_orders_list)
    month_revenue = sum(float(o.get("total_selling", 0.0)) for o in month_orders_list)
    month_profit = sum(float(o.get("total_profit", 0.0)) for o in month_orders_list)

    breakdown_map = {}
    channel_map = {}
    for o in orders:
        s_name = o.get("store_name", "Other")
        if s_name not in breakdown_map:
            breakdown_map[s_name] = [0, 0.0, 0.0]
        breakdown_map[s_name][0] += 1
        breakdown_map[s_name][1] += float(o.get("total_selling", 0.0))
        breakdown_map[s_name][2] += float(o.get("total_profit", 0.0))
        channel = o.get("channel", "Other")
        channel_map[channel] = channel_map.get(channel, 0) + 1

    store_breakdown = [
        (s, data[0], data[1], data[2]) for s, data in breakdown_map.items()
    ]
    channel_breakdown = [
        (channel, count) for channel, count in sorted(channel_map.items())
    ]

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "today_profit": today_profit,
        "month_orders": month_orders,
        "month_revenue": month_revenue,
        "month_profit": month_profit,
        "store_breakdown": store_breakdown,
        "channel_breakdown": channel_breakdown,
        "low_stock_count": sum(1 for p in products if 0 < p.get("stock", 0) <= 3),
        "out_of_stock_count": sum(1 for p in products if p.get("stock", 0) <= 0)
    }
