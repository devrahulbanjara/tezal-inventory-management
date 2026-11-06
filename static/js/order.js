// Tezal's Inventory Management & Bill Generator Client JS

document.addEventListener("DOMContentLoaded", function () {
  // 1. Searchable filter for Inventory Table
  const invSearchInput = document.getElementById("inventoryTableSearch");
  if (invSearchInput) {
    invSearchInput.addEventListener("input", function () {
      const filter = this.value.toLowerCase().trim();
      const rows = document.querySelectorAll("#inventoryTable tbody tr");
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? "" : "none";
      });
    });
  }

  // 2. New Order Dynamic Items Management
  const itemsContainer = document.getElementById("orderItemsContainer");
  const addItemBtn = document.getElementById("addItemBtn");

  if (itemsContainer && addItemBtn) {
    let availableProducts = [];

    // Fetch products list from API for autocomplete & auto-pricing
    fetch("/api/products")
      .then(res => res.json())
      .then(data => {
        availableProducts = data;
        // Populate existing select inputs
        document.querySelectorAll(".product-select").forEach(select => {
          populateSelectOptions(select, availableProducts);
        });
        updateOrderSummary();
      })
      .catch(err => console.error("Error fetching products:", err));

    function populateSelectOptions(selectElement, products) {
      const currentVal = selectElement.value || selectElement.dataset.selected || "";
      selectElement.innerHTML = `<option value="">-- Choose Product Code --</option>`;
      products.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.code;
        opt.textContent = `${p.code} - ${p.name} (Stock: ${p.stock}, Rs. ${p.selling_price})`;
        opt.dataset.name = p.name;
        opt.dataset.cp = p.cost_price;
        opt.dataset.sp = p.selling_price;
        opt.dataset.stock = p.stock;
        if (p.code === currentVal) {
          opt.selected = true;
        }
        selectElement.appendChild(opt);
      });
    }

    // Add new item row
    addItemBtn.addEventListener("click", function () {
      const rowId = "row_" + Date.now();
      const row = document.createElement("div");
      row.className = "item-row";
      row.id = rowId;
      row.innerHTML = `
        <div class="item-row-grid">
          <div>
            <label class="form-label">Product / Code</label>
            <select name="product_code[]" class="form-control product-select" required>
              <option value="">-- Choose Product Code --</option>
            </select>
            <input type="hidden" name="product_name[]" class="input-prod-name" value="">
          </div>
          <div>
            <label class="form-label">Quantity</label>
            <input type="number" name="quantity[]" class="form-control input-qty" value="1" min="1" step="1" required inputmode="numeric">
          </div>
          <div>
            <label class="form-label">Selling Price (Rs.)</label>
            <input type="number" step="any" name="selling_price[]" class="form-control input-sp" value="0" min="0" required inputmode="decimal">
          </div>
          <div>
            <label class="form-label">Cost Price (Rs.)</label>
            <input type="number" step="any" name="cost_price[]" class="form-control input-cp" value="0" min="0" required inputmode="decimal" title="Internal cost to calculate profit">
          </div>
          <div>
            <label class="form-label">Line Total</label>
            <div class="form-control line-total" style="background:#F1F5F9; font-weight:600; text-align:right;">Rs. 0</div>
          </div>
          <div style="text-align: center; margin-top: 1.5rem;">
            <button type="button" class="btn btn-danger-outline btn-sm btn-remove-row" title="Remove item">✕</button>
          </div>
        </div>
      `;
      itemsContainer.appendChild(row);

      const select = row.querySelector(".product-select");
      populateSelectOptions(select, availableProducts);
      attachRowEvents(row);
      updateOrderSummary();
    });

    function attachRowEvents(row) {
      const select = row.querySelector(".product-select");
      const nameInput = row.querySelector(".input-prod-name");
      const qtyInput = row.querySelector(".input-qty");
      const spInput = row.querySelector(".input-sp");
      const cpInput = row.querySelector(".input-cp");
      const totalDisplay = row.querySelector(".line-total");
      const removeBtn = row.querySelector(".btn-remove-row");

      select.addEventListener("change", function () {
        const selectedOpt = this.options[this.selectedIndex];
        if (selectedOpt && selectedOpt.value) {
          nameInput.value = selectedOpt.dataset.name || "";
          spInput.value = selectedOpt.dataset.sp || "0";
          cpInput.value = selectedOpt.dataset.cp || "0";
        } else {
          nameInput.value = "";
          spInput.value = "0";
          cpInput.value = "0";
        }
        recalculateRow(row);
        updateOrderSummary();
      });

      qtyInput.addEventListener("input", function () {
        recalculateRow(row);
        updateOrderSummary();
      });

      spInput.addEventListener("input", function () {
        recalculateRow(row);
        updateOrderSummary();
      });

      cpInput.addEventListener("input", function () {
        recalculateRow(row);
        updateOrderSummary();
      });

      if (removeBtn) {
        removeBtn.addEventListener("click", function () {
          const allRows = itemsContainer.querySelectorAll(".item-row");
          if (allRows.length > 1) {
            row.remove();
            updateOrderSummary();
          } else {
            alert("At least one product item is required for the bill.");
          }
        });
      }
    }

    function recalculateRow(row) {
      const qty = parseFloat(row.querySelector(".input-qty").value) || 0;
      const sp = parseFloat(row.querySelector(".input-sp").value) || 0;
      const lineTotal = qty * sp;
      const totalDisplay = row.querySelector(".line-total");
      if (totalDisplay) {
        totalDisplay.textContent = `Rs. ${lineTotal.toLocaleString()}`;
      }
    }

    function updateOrderSummary() {
      const rows = itemsContainer.querySelectorAll(".item-row");
      let totalQty = 0;
      let totalBill = 0;
      let totalCost = 0;
      const deliveryInput = document.getElementById("delivery_charge");
      const deliveryCharge = deliveryInput ? Math.max(0, parseFloat(deliveryInput.value) || 0) : 0;

      rows.forEach(row => {
        const qty = parseFloat(row.querySelector(".input-qty").value) || 0;
        const sp = parseFloat(row.querySelector(".input-sp").value) || 0;
        const cp = parseFloat(row.querySelector(".input-cp").value) || 0;
        totalQty += qty;
        totalBill += qty * sp;
        totalCost += qty * cp;
      });

      const netProfit = totalBill - totalCost;

      const summaryQty = document.getElementById("summaryQty");
      const summaryBill = document.getElementById("summaryBill");
      const summaryCost = document.getElementById("summaryCost");
      const summaryProfit = document.getElementById("summaryProfit");
      const summaryDelivery = document.getElementById("summaryDelivery");

      if (summaryQty) summaryQty.textContent = totalQty;
      if (summaryBill) summaryBill.textContent = `Rs. ${totalBill.toLocaleString()}`;
      if (summaryCost) summaryCost.textContent = `Rs. ${totalCost.toLocaleString()}`;
      if (summaryDelivery) summaryDelivery.textContent = `Rs. ${deliveryCharge.toLocaleString()}`;
      const customerTotal = totalBill + deliveryCharge;
      if (summaryBill) summaryBill.textContent = `Rs. ${customerTotal.toLocaleString()}`;
      if (summaryProfit) {
        summaryProfit.textContent = `Rs. ${netProfit.toLocaleString()}`;
        if (netProfit < 0) {
          summaryProfit.style.color = "#F87171";
        } else {
          summaryProfit.style.color = "#4ADE80";
        }
      }
    }

    // Attach events to the first initial row
    document.querySelectorAll(".item-row").forEach(attachRowEvents);
    const deliveryInput = document.getElementById("delivery_charge");
    if (deliveryInput) deliveryInput.addEventListener("input", updateOrderSummary);
  }
});
