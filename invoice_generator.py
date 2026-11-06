import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Base directory for bills
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BILL_DIR = os.path.join(BASE_DIR, "bill")
BRAND_DIR = os.path.join(BASE_DIR, "static", "brand")

def get_font(size=14, bold=False):
    """
    Attempts to load a clean TrueType font across Windows, macOS, and Linux,
    falling back reliably to Pillow's built-in default font.
    """
    windir = os.environ.get("WINDIR", r"C:\Windows")
    
    candidates = [
        # Windows
        os.path.join(windir, "Fonts", "arialbd.ttf" if bold else "arial.ttf"),
        os.path.join(windir, "Fonts", "segoeuib.ttf" if bold else "segoeui.ttf"),
        os.path.join(windir, "Fonts", "calibrib.ttf" if bold else "calibri.ttf"),
        
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        
        # Generic name lookups
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans.ttf",
    ]
    
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def generate_invoice_image(order_data):
    """
    Generates a clean digital invoice image for an order.
    Partitions output by date: bill/YYYY/MM/DD/{invoice_no}.png
    Works identically on Windows, Mac, and Linux.
    """
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")

    # Date-wise partitioned directory on disk: bill/YYYY/MM/DD/
    partitioned_dir = os.path.join(BILL_DIR, year, month, day)
    os.makedirs(partitioned_dir, exist_ok=True)

    invoice_no = order_data["invoice_no"]
    file_name = f"{invoice_no}.png"
    absolute_image_path = os.path.join(partitioned_dir, file_name)
    
    # Use forward slashes for web URL path so it works identically on Windows and Unix
    relative_image_path = f"bill/{year}/{month}/{day}/{file_name}"

    store_name = order_data.get("store_name", "Mero Choice Nepal")
    is_wardrobe = "wardrobe" in store_name.lower()

    # Customer-facing bills use a neutral professional palette. Brand identity
    # comes from the selected store logo rather than a saturated background.
    accent_color = (40, 43, 48)
    accent_light = (246, 247, 249)
    badge_color = (82, 87, 95)
    ig_handle = "@merowardrobe_nepal" if is_wardrobe else "@merochoicenepal"

    charcoal = (35, 38, 43)
    text_muted = (100, 105, 115)
    border_color = (226, 232, 240)
    white = (255, 255, 255)

    width = 760
    items = order_data.get("items", [])
    
    # Dynamic height calculation
    header_h = 130
    meta_bar_h = 45
    customer_box_h = 120
    table_header_h = 40
    rows_h = max(len(items), 1) * 44
    totals_h = 120
    footer_h = 110
    padding = 40
    
    total_height = header_h + meta_bar_h + customer_box_h + table_header_h + rows_h + totals_h + footer_h + padding

    image = Image.new("RGB", (width, total_height), color=white)
    draw = ImageDraw.Draw(image)

    # Fonts
    font_brand = get_font(26, bold=True)
    font_sub = get_font(12, bold=False)
    font_sec_title = get_font(13, bold=True)
    font_body = get_font(13, bold=False)
    font_body_bold = get_font(13, bold=True)
    font_table_hdr = get_font(12, bold=True)
    font_big_total = get_font(18, bold=True)
    font_inv_badge = get_font(14, bold=True)

    # 1. Header Banner
    draw.rectangle([(0, 0), (width, header_h)], fill=accent_color)

    logo_name = "mero-wardrobe-nepal.jpg" if is_wardrobe else "mero-choice-nepal.jpg"
    logo_path = os.path.join(BRAND_DIR, logo_name)
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGB")
            logo.thumbnail((62, 62))
            logo_x = 40
            logo_y = (header_h - logo.height) // 2
            image.paste(logo, (logo_x, logo_y))
            brand_x = logo_x + logo.width + 16
        except Exception:
            brand_x = 40
    else:
        brand_x = 40
    
    # Store title
    draw.text((brand_x, 30), store_name.upper(), fill=white, font=font_brand)
    draw.text((brand_x + 2, 70), "ORDER RECEIPT", fill=(245, 245, 245), font=font_sub)
    draw.text((brand_x + 2, 88), f"Kathmandu, Nepal  |  {ig_handle}", fill=(230, 230, 230), font=font_sub)

    # Invoice Badge Top Right
    badge_x = width - 230
    draw.rounded_rectangle([(badge_x, 30), (width - 40, 95)], radius=8, fill=badge_color)
    draw.text((badge_x + 15, 40), "INVOICE", fill=white, font=font_sec_title)
    draw.text((badge_x + 15, 62), invoice_no, fill=white, font=font_inv_badge)

    # 2. Meta Strip (Date & Payment)
    y = header_h
    draw.rectangle([(0, y), (width, y + meta_bar_h)], fill=accent_light)
    draw.line([(0, y + meta_bar_h), (width, y + meta_bar_h)], fill=border_color, width=1)
    
    date_display = order_data.get("date_str") or now.strftime("%d %b %Y, %I:%M %p")
    draw.text((40, y + 14), f"Date: {date_display}", fill=charcoal, font=font_body_bold)
    
    pay_method = order_data.get("payment_method", "Cash on Delivery")
    pay_text = f"Payment Method: {pay_method}"
    draw.text((width - 320, y + 14), pay_text, fill=charcoal, font=font_body_bold)

    # 3. Customer Information Box
    y += meta_bar_h + 20
    draw.rounded_rectangle([(40, y), (width - 40, y + customer_box_h)], radius=6, fill=(250, 250, 252), outline=border_color, width=1)
    
    draw.text((55, y + 14), "BILLED TO / CUSTOMER DETAILS", fill=accent_color, font=font_sec_title)
    draw.line([(55, y + 36), (width - 55, y + 36)], fill=border_color, width=1)
    
    c_name = order_data.get("customer_name", "Valued Customer")
    c_address = order_data.get("customer_address", "Kathmandu, Nepal")
    c_phone = order_data.get("customer_phone", "")

    draw.text((55, y + 46), "Name:", fill=text_muted, font=font_body)
    draw.text((125, y + 46), c_name, fill=charcoal, font=font_body_bold)

    draw.text((55, y + 70), "Address:", fill=text_muted, font=font_body)
    draw.text((125, y + 70), c_address, fill=charcoal, font=font_body)

    if c_phone:
        draw.text((55, y + 92), "Contact:", fill=text_muted, font=font_body)
        draw.text((125, y + 92), c_phone, fill=charcoal, font=font_body)

    # 4. Table Header
    y += customer_box_h + 25
    table_left = 40
    table_right = width - 40
    
    draw.rectangle([(table_left, y), (table_right, y + table_header_h)], fill=accent_light)
    draw.line([(table_left, y), (table_right, y)], fill=accent_color, width=2)
    draw.line([(table_left, y + table_header_h), (table_right, y + table_header_h)], fill=border_color, width=1)

    col_code = table_left + 15
    col_name = table_left + 115
    col_qty = table_left + 420
    col_price = table_left + 500
    col_total = width - 55

    draw.text((col_code, y + 12), "CODE", fill=charcoal, font=font_table_hdr)
    draw.text((col_name, y + 12), "ITEM / DESCRIPTION", fill=charcoal, font=font_table_hdr)
    draw.text((col_qty, y + 12), "QTY", fill=charcoal, font=font_table_hdr)
    draw.text((col_price, y + 12), "PRICE", fill=charcoal, font=font_table_hdr)
    
    bbox_tot = draw.textbbox((0, 0), "TOTAL", font=font_table_hdr)
    draw.text((col_total - (bbox_tot[2] - bbox_tot[0]), y + 12), "TOTAL", fill=charcoal, font=font_table_hdr)

    # 5. Table Rows
    y += table_header_h
    row_h = 42

    for idx, item in enumerate(items):
        row_y = y + (idx * row_h)
        bg = (255, 255, 255) if idx % 2 == 0 else (252, 252, 254)
        draw.rectangle([(table_left, row_y), (table_right, row_y + row_h)], fill=bg)
        draw.line([(table_left, row_y + row_h), (table_right, row_y + row_h)], fill=border_color, width=1)

        code_str = str(item.get("product_code", ""))
        name_str = str(item.get("product_name", ""))
        qty_str = str(item.get("quantity", 1))
        price_num = float(item.get("selling_price", 0.0))
        subtotal_num = float(item.get("subtotal", price_num * int(qty_str)))

        draw.text((col_code, row_y + 12), code_str, fill=accent_color, font=font_body_bold)
        
        if len(name_str) > 34:
            name_str = name_str[:32] + "..."
        draw.text((col_name, row_y + 12), name_str, fill=charcoal, font=font_body)
        
        draw.text((col_qty + 5, row_y + 12), qty_str, fill=charcoal, font=font_body)
        draw.text((col_price, row_y + 12), f"Rs. {price_num:,.0f}", fill=text_muted, font=font_body)

        tot_text = f"Rs. {subtotal_num:,.0f}"
        b_t = draw.textbbox((0, 0), tot_text, font=font_body_bold)
        draw.text((col_total - (b_t[2] - b_t[0]), row_y + 12), tot_text, fill=charcoal, font=font_body_bold)

    y += len(items) * row_h + 15

    # 6. Totals Box
    total_selling = float(order_data.get("total_selling", 0.0))
    delivery_charge = float(order_data.get("delivery_charge", 0.0))
    grand_total = total_selling + delivery_charge
    total_items = sum(int(item.get("quantity", 1)) for item in items)
    
    tot_box_w = 340
    tot_box_left = width - 40 - tot_box_w
    tot_box_top = y
    tot_box_bottom = y + 90

    draw.rounded_rectangle(
        [(tot_box_left, tot_box_top), (width - 40, tot_box_bottom)],
        radius=6,
        fill=accent_light,
        outline=accent_color,
        width=1
    )

    draw.text((tot_box_left + 20, tot_box_top + 10), f"Total Items: {total_items}", fill=text_muted, font=font_body)
    draw.text((tot_box_left + 20, tot_box_top + 32), "Products:", fill=text_muted, font=font_body)
    draw.text((width - 210, tot_box_top + 32), f"Rs. {total_selling:,.0f}", fill=charcoal, font=font_body)
    draw.text((tot_box_left + 20, tot_box_top + 52), "Delivery:", fill=text_muted, font=font_body)
    draw.text((width - 210, tot_box_top + 52), f"Rs. {delivery_charge:,.0f}", fill=charcoal, font=font_body)
    
    grand_label = "Grand Total:"
    grand_val = f"Rs. {grand_total:,.0f}"
    draw.text((tot_box_left + 20, tot_box_top + 72), grand_label, fill=charcoal, font=font_sec_title)
    
    b_gv = draw.textbbox((0, 0), grand_val, font=font_big_total)
    draw.text((width - 55 - (b_gv[2] - b_gv[0]), tot_box_top + 68), grand_val, fill=accent_color, font=font_big_total)

    # 7. Order Footer & Unboxing Policy Note
    y = tot_box_bottom + 30
    draw.line([(40, y), (width - 40, y)], fill=border_color, width=1)
    
    y += 18
    f_center = width // 2
    
    note_1 = "Thank you for your order."
    b_n1 = draw.textbbox((0, 0), note_1, font=font_sec_title)
    draw.text((f_center - (b_n1[2] - b_n1[0]) // 2, y), note_1, fill=accent_color, font=font_sec_title)

    y += 24
    note_2 = "Kindly record an unboxing video upon arrival for any exchange/claim inquiries."
    b_n2 = draw.textbbox((0, 0), note_2, font=font_sub)
    draw.text((f_center - (b_n2[2] - b_n2[0]) // 2, y), note_2, fill=text_muted, font=font_sub)

    y += 18
    note_3 = f"Contact: {ig_handle}"
    b_n3 = draw.textbbox((0, 0), note_3, font=font_sub)
    draw.text((f_center - (b_n3[2] - b_n3[0]) // 2, y), note_3, fill=text_muted, font=font_sub)

    image.save(absolute_image_path, "PNG", quality=95)
    return relative_image_path, absolute_image_path
