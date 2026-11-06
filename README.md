# Tezal's inventory workspace
### Custom Built for **Mero Choice Nepal** & **Mero Wardrobe Nepal**

A clean, lightweight, and custom inventory management and digital billing web application built specifically for Tezal's business operations.

---

## 🌟 Highlights

- **Pure Simplicity**: Built with **FastAPI** and direct **JSON file storage** (`data/products.json` and `data/orders.json`). No SQLite, no database servers, and no unnecessary multi-threading.
- **Cross-Platform**: Runs seamlessly on **Windows, macOS, and Linux**.
  - Windows: Double-click [`run.bat`](file:///Users/rahuldevbanjara/Documents/Personal%20Projects/Tezal's%20Inventory%20Management/run.bat) or run `python run.py`.
  - Mac / Linux: Run [`./run.sh`](file:///Users/rahuldevbanjara/Documents/Personal%20Projects/Tezal's%20Inventory%20Management/run.sh) or `python3 run.py`.
- **Inline Field Validation**:
  - Errors appear directly under the field as Tezal fills the form — before anything is saved.
  - Checks required fields, valid prices, whole-number stock, duplicate product codes, valid phone/handle, and stock limits while adding order items.
- **Custom Product Codes**:
  - Add products with custom codes like `R-001` for Ring 1, `R-002` for Ring 2, `N-001` for Necklaces, etc.
  - Set Cost Price (purchase cost) and Selling Price (retail price).
  - Stock tracking with automatic deduction on orders.
  - Instant client-side search to filter products by code or name without page reloads.
- **Orders & digital bills**:
  - **Store Brand Selector**: Easily toggle between **Mero Choice Nepal** and **Mero Wardrobe Nepal**.
  - **Sales channel**: Instagram, WhatsApp, or Other.
  - **Customer Details**: Name, delivery address, and contact / handle.
  - **Product Picker Dropdown**: Searchable product selection with auto-filling prices and stock checks.
  - **Payment Methods**: Cash on Delivery (COD), eSewa, Khalti, Bank Transfer, Paid Online.
  - **Live Profit Calculator**: Real-time display of total cost, customer bill, and net profit before generating.
- **High-Resolution Bill Images**:
  - Automatically renders a digital bill as a **PNG image** ready to DM directly on Instagram, WhatsApp, or Viber.
  - **Date-Partitioned Organization**: Saved automatically in a date-wise structure:
    ```
    bill/
    └── 2026/
        └── 11/
            └── 05/
                ├── INV-20261105-001.png
                └── INV-20261105-002.png
    ```
- **Sales & Orders Dashboard**:
  - Total Revenue, Total Cost, and Total Net Profit tracking.
  - Monthly metrics: revenue, profit, order count, and stock attention.
  - Store and channel mix on the Dashboard.
  - Store performance breakdown (Mero Choice vs Mero Wardrobe).
  - Filter orders by store or date.
  - Restores stock if an order is cancelled or deleted.

---

## 🚀 How to Run (Mac, Windows, Linux)

### On Windows 🪟
You can simply **double-click** `run.bat` in File Explorer, or open Command Prompt / PowerShell:
```cmd
run.bat
```
*(Or run `python run.py`)*

### On Mac & Linux 🍎 🐧
Open Terminal in the project folder and run:
```bash
./run.sh
```
*(Or run `python3 run.py`)*

---

### Universal Python Command (Any OS)
If you prefer running with standard Python:
```bash
# 1. Activate venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

# 2. Run
python main.py
```

Then open your web browser at:
👉 **`http://127.0.0.1:8000`**

---

## 📁 Project Structure

```text
Tezal's Inventory Management/
├── main.py                 # FastAPI application routes and controllers
├── app.py                  # Standard launcher wrapper (python app.py)
├── run.py                  # Universal cross-platform launcher (Mac, Win, Linux)
├── run.sh                  # One-click startup script for macOS & Linux
├── run.bat                 # One-click startup batch script for Windows
├── storage.py              # Simple JSON data store (products.json, orders.json)
├── invoice_generator.py    # Cross-platform Pillow bill image generator
├── requirements.txt        # Plain requirements (fastapi, uvicorn, jinja2, Pillow)
├── test_app.py             # Automated end-to-end tests
├── data/                   # Simple JSON data files (No complex database)
│   ├── products.json       # All inventory products
│   └── orders.json         # All customer orders and financial records
├── bill/                   # Date-partitioned bill images
│   └── YYYY/MM/DD/         # Everyday's bills stored in their own date folder
├── static/
│   ├── css/style.css       # Clean, modern, responsive styling
│   ├── js/order.js         # Dynamic line items & live profit calculation
│   └── js/validation.js    # Inline, real-time field validation
└── templates/
    ├── base.html           # Layout with navigation & flash alerts
    ├── dashboard.html      # Overview, stats, profit metrics & recent sales
    ├── inventory.html      # Product entry form & searchable table
    ├── edit_product.html   # Update product details & restock
    ├── new_order.html      # New order form with bill generator
    ├── bill_preview.html   # Digital bill image preview & download
    └── orders.html         # Order history & profit tracking
```

---

## 💡 How Tezal Uses It

1. **Add Inventory**: Go to **Products** (`/inventory`), type `R-001`, `Ring 1 (Floral)`, Cost `350`, Selling `650`, Stock `15`, and click Save.
2. **When a sale arrives**:
   - Click **New order** (`/orders/new`).
   - Select the shop and sales channel.
   - Pick the store: **Mero Choice Nepal** or **Mero Wardrobe Nepal**.
   - Type customer name & delivery address.
   - Pick `R-001` from the dropdown (selling and cost prices auto-populate).
   - See the real-time profit.
   - Click **Save order & generate bill**.
3. **Send to Customer**:
   - The digital invoice image appears immediately.
   - Click **⬇️ Download Bill Image (PNG)** and send it directly in the Instagram DM chat!
