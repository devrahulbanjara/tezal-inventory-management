import math
import os
import re
import urllib.parse
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import storage
import invoice_generator as ig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BILL_DIR = os.path.join(BASE_DIR, "bill")
os.makedirs(BILL_DIR, exist_ok=True)

app = FastAPI(title="Tezal's Inventory & Billing System")

# Mount static folder
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals["now"] = datetime.now

def redirect_with_flash(url: str, message: str, category: str = "info"):
    encoded_msg = urllib.parse.quote_plus(message)
    separator = "&" if "?" in url else "?"
    target = f"{url}{separator}msg={encoded_msg}&cat={category}"
    return RedirectResponse(url=target, status_code=status.HTTP_303_SEE_OTHER)

PRODUCT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")

def validate_product_fields(code: str, name: str, cost_price: float, selling_price: float, stock: int):
    """Server-side safety net; the browser shows inline errors first."""
    clean_code = code.strip().upper()
    clean_name = name.strip()

    if not clean_code:
        return "Product code is required."
    if len(clean_code) > 20:
        return "Product code must be 20 characters or fewer."
    if not PRODUCT_CODE_PATTERN.match(clean_code):
        return "Product code can only use letters, numbers and - _ / (e.g. R-001)."
    if len(clean_name) < 2:
        return "Product name must be at least 2 characters."
    if len(clean_name) > 120:
        return "Product name must be 120 characters or fewer."
    if not math.isfinite(cost_price) or not math.isfinite(selling_price):
        return "Cost and selling prices must be valid numbers."
    if cost_price < 0 or selling_price < 0:
        return "Cost and selling prices cannot be negative."
    if stock < 0:
        return "Stock quantity cannot be negative."
    return None

# ----------------- Dashboard -----------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    stats = storage.get_dashboard_stats()
    all_orders = storage.get_all_orders()
    recent_orders = all_orders[:6]
    low_stock = [p for p in storage.get_all_products() if p.get("stock", 0) <= 3]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "recent_orders": recent_orders,
            "low_stock_products": low_stock,
            "active_page": "dashboard"
        }
    )

# ----------------- Inventory Routes -----------------

@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request, q: str = ""):
    products = storage.get_all_products(search=q if q else None)
    return templates.TemplateResponse(
        request=request,
        name="inventory.html",
        context={
            "products": products,
            "existing_codes": [p["code"] for p in storage.get_all_products()],
            "search": q,
            "active_page": "inventory"
        }
    )

@app.post("/inventory/add")
async def add_product_action(
    code: str = Form(...),
    name: str = Form(...),
    cost_price: str = Form(...),
    selling_price: str = Form(...),
    stock: str = Form(...)
):
    try:
        cp = float(cost_price)
        sp = float(selling_price)
        st = int(stock)
    except ValueError:
        return redirect_with_flash("/inventory", "Invalid price or stock values. Numbers required.", "danger")

    validation_error = validate_product_fields(code, name, cp, sp, st)
    if validation_error:
        return redirect_with_flash("/inventory", validation_error, "danger")

    success, msg = storage.add_product(code, name, cp, sp, st)
    return redirect_with_flash("/inventory", msg, "success" if success else "danger")

@app.get("/inventory/edit/{product_id}", response_class=HTMLResponse)
async def edit_product_page(request: Request, product_id: int):
    product = storage.get_product_by_id(product_id)
    if not product:
        return redirect_with_flash("/inventory", "Product not found.", "danger")
    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "product": product,
            "existing_codes": [
                p["code"] for p in storage.get_all_products()
                if p.get("id") != product_id
            ],
            "active_page": "inventory"
        }
    )

@app.post("/inventory/edit/{product_id}")
async def edit_product_action(
    product_id: int,
    code: str = Form(...),
    name: str = Form(...),
    cost_price: str = Form(...),
    selling_price: str = Form(...),
    stock: str = Form(...)
):
    try:
        cp = float(cost_price)
        sp = float(selling_price)
        st = int(stock)
    except ValueError:
        return redirect_with_flash(f"/inventory/edit/{product_id}", "Invalid numeric values entered.", "danger")

    validation_error = validate_product_fields(code, name, cp, sp, st)
    if validation_error:
        return redirect_with_flash(f"/inventory/edit/{product_id}", validation_error, "danger")

    success, msg = storage.update_product(product_id, code, name, cp, sp, st)
    if success:
        return redirect_with_flash("/inventory", msg, "success")
    return redirect_with_flash(f"/inventory/edit/{product_id}", msg, "danger")

@app.post("/inventory/delete/{product_id}")
async def delete_product_action(product_id: int):
    success, msg = storage.delete_product(product_id)
    return redirect_with_flash("/inventory", msg, "info" if success else "danger")

# ----------------- Order & Bill Generation Routes -----------------

@app.get("/orders/new", response_class=HTMLResponse)
async def new_order_page(request: Request):
    products = storage.get_all_products()
    return templates.TemplateResponse(
        request=request,
        name="new_order.html",
        context={
            "products": products,
            "active_page": "orders"
        }
    )

@app.post("/orders/create")
async def create_order_action(
    store_name: str = Form("Mero Choice Nepal"),
    channel: str = Form("Other"),
    customer_name: str = Form(...),
    customer_address: str = Form(...),
    customer_phone: str = Form(""),
    payment_method: str = Form("Cash on Delivery (COD)"),
    delivery_charge: str = Form("0"),
    notes: str = Form(""),
    product_codes: list[str] = Form(..., alias="product_code[]"),
    product_names: list[str] = Form([], alias="product_name[]"),
    quantities: list[int] = Form(..., alias="quantity[]"),
    cost_prices: list[float] = Form(..., alias="cost_price[]"),
    selling_prices: list[float] = Form(..., alias="selling_price[]")
):
    c_name = customer_name.strip()
    c_address = customer_address.strip()
    if len(c_name) < 2:
        return redirect_with_flash("/orders/new", "Customer name must be at least 2 characters.", "danger")
    if len(c_name) > 100:
        return redirect_with_flash("/orders/new", "Customer name must be 100 characters or fewer.", "danger")
    if len(c_address) < 3:
        return redirect_with_flash("/orders/new", "Delivery address must be at least 3 characters.", "danger")
    if len(c_address) > 200:
        return redirect_with_flash("/orders/new", "Delivery address must be 200 characters or fewer.", "danger")
    if len(customer_phone.strip()) > 50:
        return redirect_with_flash("/orders/new", "Contact must be 50 characters or fewer.", "danger")
    if len(notes.strip()) > 200:
        return redirect_with_flash("/orders/new", "Notes must be 200 characters or fewer.", "danger")
    try:
        delivery_fee = float(delivery_charge or 0)
    except ValueError:
        return redirect_with_flash("/orders/new", "Delivery charge must be a valid number.", "danger")
    if not math.isfinite(delivery_fee) or delivery_fee < 0:
        return redirect_with_flash("/orders/new", "Delivery charge cannot be negative.", "danger")

    items = []
    total_selling = 0.0
    total_cost = 0.0

    for i in range(len(product_codes)):
        code = str(product_codes[i]).strip().upper()
        if not code:
            continue
        try:
            qty = int(quantities[i])
            cp = float(cost_prices[i])
            sp = float(selling_prices[i])
        except (ValueError, IndexError):
            continue

        if qty < 1:
            return redirect_with_flash("/orders/new", "Every item quantity must be at least 1.", "danger")
        if not math.isfinite(cp) or not math.isfinite(sp) or cp < 0 or sp < 0:
            return redirect_with_flash("/orders/new", "Item prices must be valid, non-negative numbers.", "danger")

        name = str(product_names[i]).strip() if i < len(product_names) else code
        subtot = round(sp * qty, 2)
        total_selling += subtot
        total_cost += round(cp * qty, 2)

        items.append({
            "product_code": code,
            "product_name": name,
            "quantity": qty,
            "cost_price": cp,
            "selling_price": sp,
            "subtotal": subtot
        })

    if not items:
        return redirect_with_flash("/orders/new", "Please add at least one product to the order.", "danger")

    # Generate sequential invoice number
    invoice_no = storage.generate_invoice_no()

    # Generate Image Bill partitioned by date in folder named 'bill': bill/YYYY/MM/DD/{invoice_no}.png
    now = datetime.now()
    bill_data = {
        "invoice_no": invoice_no,
        "store_name": store_name.strip(),
        "customer_name": c_name,
        "customer_address": c_address,
        "customer_phone": customer_phone.strip(),
        "payment_method": payment_method.strip(),
        "items": items,
        "total_selling": total_selling,
        "delivery_charge": delivery_fee,
        "grand_total": round(total_selling + delivery_fee, 2),
        "date_str": now.strftime("%d %b %Y, %I:%M %p")
    }

    rel_image_path, _ = ig.generate_invoice_image(bill_data)

    # Save to JSON storage and decrement stock
    order_id, _ = storage.create_order(
        store_name=store_name.strip(),
        customer_name=c_name,
        customer_address=c_address,
        customer_phone=customer_phone.strip(),
        payment_method=payment_method.strip(),
        notes=notes.strip(),
        items=items,
        bill_image_path=rel_image_path,
        channel=channel.strip(),
        delivery_charge=delivery_fee
    )

    return redirect_with_flash(f"/orders/{order_id}", f"Order {invoice_no} created and digital bill generated!", "success")

@app.get("/orders/{order_id}", response_class=HTMLResponse)
async def view_order_page(request: Request, order_id: int):
    order = storage.get_order_by_id(order_id)
    if not order:
        return redirect_with_flash("/orders", "Order not found.", "danger")
    return templates.TemplateResponse(
        request=request,
        name="bill_preview.html",
        context={
            "order": order,
            "active_page": "orders"
        }
    )

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request, store: str = "all", channel: str = "all", date: str = ""):
    orders = storage.get_all_orders(store_filter=store, channel_filter=channel, date_filter=date)
    stats = storage.get_dashboard_stats()
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "orders": orders,
            "store_filter": store,
            "channel_filter": channel,
            "date_filter": date,
            "stats": stats,
            "active_page": "orders"
        }
    )

@app.post("/orders/delete/{order_id}")
async def delete_order_action(order_id: int):
    success = storage.delete_order(order_id)
    if success:
        return redirect_with_flash("/orders", f"Order #{order_id} deleted and stock restored to inventory.", "info")
    return redirect_with_flash("/orders", "Could not delete order.", "danger")

# ----------------- Serving Partitioned Bill Images -----------------

@app.get("/bill/{year}/{month}/{day}/{filename}")
async def serve_bill_image(year: str, month: str, day: str, filename: str, download: int = 0):
    """
    Serves the partitioned bill image from bill/YYYY/MM/DD/filename.
    If ?download=1 is provided, triggers a file download header.
    """
    filepath = os.path.join(BILL_DIR, year, month, day, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Bill image not found on server")
    
    headers = {}
    if download == 1:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        
    return FileResponse(filepath, media_type="image/png", headers=headers)

# ----------------- API Endpoints -----------------

@app.get("/api/products")
async def api_products():
    """Returns JSON products list for frontend autocomplete."""
    products = storage.get_all_products()
    return JSONResponse(content=[
        {
            "id": p["id"],
            "code": p["code"],
            "name": p["name"],
            "cost_price": p["cost_price"],
            "selling_price": p["selling_price"],
            "stock": p["stock"]
        } for p in products
    ])

# ----------------- App Runner -----------------

if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("✨ Tezal's Inventory Management System ✨")
    print("🚀 FastAPI Server starting...")
    print("📍 Local URL: http://127.0.0.1:8000")
    print("📁 Digital bills saved in: bill/YYYY/MM/DD/")
    print("💾 Data stored simply in: data/products.json and data/orders.json")
    print("=" * 65)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
