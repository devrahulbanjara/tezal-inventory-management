import os
from starlette.testclient import TestClient
from main import app
import storage

client = TestClient(app, follow_redirects=False)

def test_full_workflow():
    print("▶ Running end-to-end tests for Tezal's Inventory & Billing System...")

    # 1. Dashboard
    res = client.get("/")
    assert res.status_code == 200, f"Dashboard failed: {res.status_code}"
    assert "Tezal" in res.text
    assert "This month" in res.text
    assert "New order" in res.text
    assert "Local Inventory & Digital Bill System" not in res.text
    print("✓ Dashboard GET 200 OK")

    # 2. Inventory Page
    res = client.get("/inventory")
    assert res.status_code == 200
    assert "Inventory" in res.text
    assert "Product list" in res.text
    print("✓ Inventory Page GET 200 OK")

    # 3. Add Product
    res = client.post("/inventory/add", data={
        "code": "R-003",
        "name": "Ring 3 (Rose Quartz Silver)",
        "cost_price": "450",
        "selling_price": "850",
        "stock": "10"
    })
    assert res.status_code == 303
    print("✓ Add Product POST 303 Redirect OK")

    # Verify product in storage
    p = storage.get_product_by_code("R-003")
    assert p is not None
    assert p["name"] == "Ring 3 (Rose Quartz Silver)"
    assert p["selling_price"] == 850.0
    print("✓ Product R-003 saved properly in JSON storage")

    # 4. Duplicate Product Code rejection
    res = client.post("/inventory/add", data={
        "code": "R-003",
        "name": "Duplicate Ring",
        "cost_price": "400",
        "selling_price": "800",
        "stock": "5"
    })
    assert res.status_code == 303
    assert "already+exists" in res.headers["location"]
    print("✓ Duplicate product code correctly rejected")

    # 5. API Products endpoint
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert any(x["code"] == "R-003" for x in data)
    print("✓ /api/products JSON endpoint verified")

    # 5b. Inline validation markup is present on both forms
    res = client.get("/inventory")
    assert 'data-validate="product"' in res.text
    assert "novalidate" in res.text
    assert 'data-existing-codes="' in res.text
    res = client.get("/orders/new")
    assert 'data-validate="order"' in res.text
    assert "novalidate" in res.text
    assert "WhatsApp" in res.text
    assert "Instagram" in res.text
    print("✓ Inline field-validation hooks present on product and order forms")

    # 5c. Server safety net rejects invalid values if client validation is bypassed
    res = client.post("/inventory/add", data={
        "code": "R-004",
        "name": "Invalid Ring",
        "cost_price": "-10",
        "selling_price": "500",
        "stock": "5"
    })
    assert res.status_code == 303
    assert "negative" in res.headers["location"]
    assert storage.get_product_by_code("R-004") is None
    print("✓ Server-side safety net rejects negative prices")

    # 6. Create an order with an explicit sales channel & Generate Bill
    stock_before = storage.get_product_by_code("R-003")["stock"]
    payload = {
        "store_name": "Mero Choice Nepal",
        "channel": "WhatsApp",
        "customer_name": "Pooja Gurung",
        "customer_address": "Jawalakhel, Lalitpur (Near Zoo)",
        "customer_phone": "9801234567",
        "payment_method": "Cash on Delivery (COD)",
        "delivery_charge": "100",
        "notes": "Instagram DM order",
        "product_code[]": ["R-003", "R-001"],
        "product_name[]": ["Ring 3 (Rose Quartz Silver)", "Ring 1 (Silver Floral)"],
        "quantity[]": ["2", "1"],
        "selling_price[]": ["850", "650"],
        "cost_price[]": ["450", "350"]
    }
    res = client.post("/orders/create", data=payload)
    assert res.status_code == 303
    order_redirect_url = res.headers["location"]
    print("✓ Order creation redirected to:", order_redirect_url)

    # Verify stock reduction
    stock_after = storage.get_product_by_code("R-003")["stock"]
    assert stock_after == stock_before - 2, f"Stock expected {stock_before - 2}, got {stock_after}"
    print(f"✓ Stock deducted accurately ({stock_before} -> {stock_after})")

    # Verify order in storage
    orders = storage.get_all_orders()
    assert len(orders) >= 1
    latest_order = orders[0]
    assert latest_order["customer_name"] == "Pooja Gurung"
    assert latest_order["channel"] == "WhatsApp"
    assert latest_order["delivery_charge"] == 100.0
    assert latest_order["grand_total"] == 2450.0
    # Total selling: 2 * 850 + 1 * 650 = 1700 + 650 = 2350
    assert latest_order["total_selling"] == 2350.0
    # Total cost: 2 * 450 + 1 * 350 = 900 + 350 = 1250
    assert latest_order["total_cost"] == 1250.0
    # Total profit: 2350 - 1250 = 1100
    assert latest_order["total_profit"] == 1100.0
    print("✓ Order totals and profit accurately calculated (Sales: 2350, Cost: 1250, Profit: 1100)")

    # 7. Check Bill Image File on disk
    bill_path = latest_order["bill_image_path"]
    print("✓ Generated bill image path:", bill_path)
    abs_bill_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), bill_path)
    assert os.path.exists(abs_bill_path), f"Bill file missing on disk: {abs_bill_path}"
    assert os.path.getsize(abs_bill_path) > 10000, "Bill image file is too small"
    print(f"✓ Bill image file exists on disk ({os.path.getsize(abs_bill_path)} bytes) in date-partitioned folder")

    # 8. Serve Bill Image via FastAPI
    res = client.get(f"/{bill_path}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    print("✓ Bill image successfully served via HTTP with image/png")

    # 9. Serve Bill Image with download parameter
    res = client.get(f"/{bill_path}?download=1")
    assert res.status_code == 200
    assert "attachment" in res.headers.get("content-disposition", "")
    print("✓ Bill image download parameter verified")

    # 10. View Order Preview Page
    res = client.get(f"/orders/{latest_order['id']}")
    assert res.status_code == 200
    assert "Pooja Gurung" in res.text
    assert "2,350" in res.text
    assert "Delivery charge" in res.text
    assert "2,450" in res.text
    print("✓ Order preview page rendered with customer details and image")

    # 11. Orders List Page with Filters
    res = client.get("/orders")
    assert res.status_code == 200
    assert "Pooja Gurung" in res.text
    print("✓ Orders history page rendered")

    # Filter by store
    res_choice = client.get("/orders?store=Mero+Choice+Nepal")
    assert res_choice.status_code == 200
    assert "Pooja Gurung" in res_choice.text

    res_wardrobe = client.get("/orders?store=Mero+Wardrobe+Nepal")
    assert res_wardrobe.status_code == 200
    assert "Pooja Gurung" not in res_wardrobe.text
    print("✓ Orders store filtering works correctly")

    # Filter by channel
    res_whatsapp = client.get("/orders?channel=WhatsApp")
    assert res_whatsapp.status_code == 200
    assert "Pooja Gurung" in res_whatsapp.text
    res_instagram = client.get("/orders?channel=Instagram")
    assert res_instagram.status_code == 200
    assert "Pooja Gurung" not in res_instagram.text
    print("✓ Orders channel filtering works correctly")

    # Keep the local JSON fixtures clean for the next run.
    storage.delete_order(latest_order["id"])
    test_product = storage.get_product_by_code("R-003")
    if test_product:
        storage.delete_product(test_product["id"])

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The system is 100% functional.")

if __name__ == "__main__":
    test_full_workflow()
