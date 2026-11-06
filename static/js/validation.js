// Inline, real-time field validation for Tezal's Inventory Management System.
// Errors appear next to the field, before the form is ever submitted.
// Server-side checks remain as a final safety net.

(function () {
  "use strict";

  let errorCounter = 0;

  function isBlank(value) {
    return !value || !String(value).trim();
  }

  function fieldWrapper(field) {
    return field.closest(".form-group") || field.parentElement || field;
  }

  function showError(field, message) {
    const wrapper = fieldWrapper(field);
    field.classList.add("is-invalid");
    field.setAttribute("aria-invalid", "true");

    let errorNode = wrapper.querySelector(":scope > .field-error");
    if (!errorNode) {
      errorNode = document.createElement("div");
      errorNode.className = "field-error";
      errorNode.setAttribute("role", "alert");
      errorNode.id = "field-error-" + (++errorCounter);
      wrapper.appendChild(errorNode);
    }

    errorNode.textContent = message;
    field.setAttribute("aria-describedby", errorNode.id);
  }

  function clearError(field) {
    field.classList.remove("is-invalid");
    field.removeAttribute("aria-invalid");

    const wrapper = fieldWrapper(field);
    const errorNode = wrapper.querySelector(":scope > .field-error");
    if (errorNode) {
      errorNode.remove();
    }
    field.removeAttribute("aria-describedby");
  }

  /**
   * Wires up a form with delegated events so dynamically added order rows
   * are validated too.
   *
   * @param {HTMLFormElement} form
   * @param {(form: HTMLFormElement) => Array<{field: HTMLElement, validate: () => string|null}>} buildValidators
   */
  function setupValidation(form, buildValidators) {
    if (!form || form.dataset.validationReady === "1") {
      return;
    }
    form.dataset.validationReady = "1";

    const touched = new WeakSet();
    let attempted = false;

    const banner = document.createElement("div");
    banner.className = "form-error-banner";
    banner.setAttribute("role", "alert");
    banner.setAttribute("aria-live", "polite");
    form.prepend(banner);

    function refresh(forceDisplay) {
      const results = buildValidators(form);

      results.forEach(({ field, validate }) => {
        const error = validate();
        if (!error) {
          clearError(field);
          return;
        }
        if (forceDisplay || attempted || touched.has(field)) {
          showError(field, error);
        }
      });

      const errors = results
        .map(({ field, validate }) => ({ field, error: validate() }))
        .filter((entry) => entry.error);

      return {
        valid: errors.length === 0,
        count: errors.length,
        firstField: errors.length ? errors[0].field : null,
      };
    }

    function handleFieldEvent(event, markTouched) {
      const target = event.target;
      if (!(target instanceof HTMLElement) || !form.contains(target)) {
        return;
      }
      if (!target.matches("input, select, textarea")) {
        return;
      }
      if (target.type === "hidden" || target.disabled) {
        return;
      }

      if (markTouched) {
        touched.add(target);
      } else if (!touched.has(target) && !attempted) {
        return;
      }

      const { valid } = refresh(false);
      if (valid) {
        banner.classList.remove("is-visible");
      }
    }

    // Validate when the user leaves a field (not while they are still typing).
    form.addEventListener("focusout", (event) => handleFieldEvent(event, true));

    // Once a field has been touched, clear or update its message live.
    form.addEventListener("input", (event) => handleFieldEvent(event, false));

    form.addEventListener("change", (event) => {
      // Selecting a value is a deliberate action, so validate selects immediately.
      if (event.target instanceof HTMLSelectElement) {
        handleFieldEvent(event, true);
      } else {
        handleFieldEvent(event, false);
      }
    });

    form.addEventListener("submit", (event) => {
      attempted = true;
      const { valid, count, firstField } = refresh(true);

      if (valid) {
        banner.classList.remove("is-visible");
        return;
      }

      event.preventDefault();
      banner.textContent =
        count === 1
          ? "Please fix the highlighted field before continuing."
          : "Please fix the " + count + " highlighted fields before continuing.";
      banner.classList.add("is-visible");

      if (firstField) {
        firstField.focus({ preventScroll: true });
        firstField.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });

    // Called by other scripts when rows are added/removed.
    form.refreshValidation = () => refresh(false);
  }

  // ----------------- Shared field rules -----------------

  function validateRequiredText(field, label, minLength, maxLength) {
    const value = field.value.trim();
    if (!value) {
      return label + " is required.";
    }
    if (minLength && value.length < minLength) {
      return label + " must be at least " + minLength + " characters.";
    }
    if (maxLength && value.length > maxLength) {
      return label + " must be " + maxLength + " characters or fewer.";
    }
    return null;
  }

  function validateMoney(field, label) {
    const raw = field.value.trim();
    if (!raw) {
      return label + " is required.";
    }
    const value = Number(raw);
    if (!Number.isFinite(value)) {
      return label + " must be a valid number.";
    }
    if (value < 0) {
      return label + " cannot be negative.";
    }
    if (value > 100000000) {
      return label + " looks too large. Please check it.";
    }
    return null;
  }

  function validateStock(field) {
    const raw = field.value.trim();
    if (!raw) {
      return "Stock quantity is required.";
    }
    const value = Number(raw);
    if (!Number.isInteger(value)) {
      return "Stock must be a whole number (no decimals).";
    }
    if (value < 0) {
      return "Stock cannot be negative.";
    }
    if (value > 1000000) {
      return "Stock looks too large. Please check it.";
    }
    return null;
  }

  function validateProductCode(field, existingCodes) {
    const value = field.value.trim();
    if (!value) {
      return "Product code is required.";
    }
    if (value.length > 20) {
      return "Keep the product code to 20 characters or fewer.";
    }
    if (!/^[A-Za-z0-9][A-Za-z0-9._/-]*$/.test(value)) {
      return "Use letters, numbers and - _ / only (for example R-001).";
    }
    if (existingCodes.includes(value.toUpperCase())) {
      return "Code \u201c" + value.toUpperCase() + "\u201d is already used by another product.";
    }
    return null;
  }

  function validateContact(field) {
    const value = field.value.trim();
    if (!value) {
      return null; // Optional field.
    }
    if (value.length > 50) {
      return "Keep the phone or handle to 50 characters or fewer.";
    }

    const compactPhone = value.replace(/[\s\-()]/g, "");
    const isPhone = /^\+?\d{7,15}$/.test(compactPhone);
    const isHandle = /^@?[A-Za-z0-9._]{2,30}$/.test(value);

    if (!isPhone && !isHandle) {
      return "Enter a valid phone number or @instagram handle.";
    }
    return null;
  }

  // ----------------- Product add / edit form -----------------

  function setupProductForm(form) {
    const code = form.querySelector("#code");
    const name = form.querySelector("#name");
    const costPrice = form.querySelector("#cost_price");
    const sellingPrice = form.querySelector("#selling_price");
    const stock = form.querySelector("#stock");

    if (!code || !name || !costPrice || !sellingPrice || !stock) {
      return;
    }

    const existingCodes = (form.dataset.existingCodes || "")
      .split(",")
      .map((value) => value.trim().toUpperCase())
      .filter(Boolean);

    setupValidation(form, () => [
      { field: code, validate: () => validateProductCode(code, existingCodes) },
      { field: name, validate: () => validateRequiredText(name, "Product name", 2, 120) },
      { field: costPrice, validate: () => validateMoney(costPrice, "Cost price") },
      { field: sellingPrice, validate: () => validateMoney(sellingPrice, "Selling price") },
      { field: stock, validate: () => validateStock(stock) },
    ]);
  }

  // ----------------- New order form -----------------

  function selectedStock(select) {
    const option = select.options[select.selectedIndex];
    if (!option || !option.value) {
      return null;
    }
    const stock = Number(option.dataset.stock);
    return Number.isFinite(stock) ? stock : null;
  }

  function setupOrderForm(form) {
    const customerName = form.querySelector("#customer_name");
    const customerAddress = form.querySelector("#customer_address");
    const customerPhone = form.querySelector("#customer_phone");
    const paymentMethod = form.querySelector("#payment_method");
    const deliveryCharge = form.querySelector("#delivery_charge");
    const notes = form.querySelector("#notes");

    if (!customerName || !customerAddress || !paymentMethod) {
      return;
    }

    setupValidation(form, () => {
      const validators = [
        {
          field: customerName,
          validate: () => validateRequiredText(customerName, "Customer name", 2, 100),
        },
        {
          field: customerAddress,
          validate: () => validateRequiredText(customerAddress, "Delivery address", 3, 200),
        },
        { field: customerPhone, validate: () => validateContact(customerPhone) },
        {
          field: paymentMethod,
          validate: () => (paymentMethod.value ? null : "Choose a payment method."),
        },
        {
          field: deliveryCharge,
          validate: () => validateMoney(deliveryCharge, "Delivery charge"),
        },
        {
          field: notes,
          validate: () =>
            notes.value.trim().length > 200 ? "Notes must be 200 characters or fewer." : null,
        },
      ];

      const rows = Array.from(form.querySelectorAll(".item-row"));

      // Work out total quantity per product so split rows cannot exceed stock.
      const requestedByCode = new Map();
      const rowData = rows.map((row) => {
        const select = row.querySelector(".product-select");
        const qtyInput = row.querySelector(".input-qty");
        const spInput = row.querySelector(".input-sp");
        const cpInput = row.querySelector(".input-cp");
        const code = select ? select.value : "";
        const qtyRaw = qtyInput ? qtyInput.value.trim() : "";
        const qty = Number(qtyRaw);
        const validQty = qtyRaw !== "" && Number.isInteger(qty) && qty >= 1;

        if (code && validQty) {
          requestedByCode.set(code, (requestedByCode.get(code) || 0) + qty);
        }

        return { row, select, qtyInput, spInput, cpInput, code, qtyRaw, qty, validQty };
      });

      rowData.forEach((item) => {
        if (!item.select || !item.qtyInput || !item.spInput || !item.cpInput) {
          return;
        }

        validators.push({
          field: item.select,
          validate: () => (item.code ? null : "Choose a product for this line."),
        });

        validators.push({
          field: item.qtyInput,
          validate: () => {
            if (!item.qtyRaw) {
              return "Quantity is required.";
            }
            if (!Number.isInteger(item.qty)) {
              return "Quantity must be a whole number.";
            }
            if (item.qty < 1) {
              return "Quantity must be at least 1.";
            }

            const stock = selectedStock(item.select);
            if (item.code && stock !== null) {
              const requested = requestedByCode.get(item.code) || item.qty;
              if (stock === 0) {
                return "This product is out of stock. Restock it before selling.";
              }
              if (requested > stock) {
                return "Only " + stock + " in stock \u2014 " + requested + " requested in total.";
              }
            }
            return null;
          },
        });

        validators.push({
          field: item.spInput,
          validate: () => validateMoney(item.spInput, "Selling price"),
        });

        validators.push({
          field: item.cpInput,
          validate: () => validateMoney(item.cpInput, "Cost price"),
        });
      });

      return validators;
    });
  }

  // ----------------- Boot -----------------

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('form[data-validate="product"]').forEach(setupProductForm);
    document.querySelectorAll('form[data-validate="order"]').forEach(setupOrderForm);

    // Re-check totals when order.js adds or removes a line item.
    const orderForm = document.querySelector('form[data-validate="order"]');
    const itemsContainer = document.getElementById("orderItemsContainer");
    if (orderForm && itemsContainer && typeof orderForm.refreshValidation === "function") {
      const observer = new MutationObserver(() => orderForm.refreshValidation());
      observer.observe(itemsContainer, { childList: true });
    }
  });
})();
