# Tezal Small-Shop Workspace UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Tezal's local inventory app clean and easy for two small shops by separating Orders and Inventory, keeping analytics on the Dashboard, and recording the channel for each order.

**Architecture:** Keep FastAPI, Jinja templates, static CSS/JS, and JSON storage. Add a backward-compatible `channel` field to order records and a small analytics aggregation for dashboard/store/channel summaries. Rebuild the primary templates around reusable CSS classes rather than adding a frontend framework.

**Tech Stack:** Python, FastAPI, Jinja2, JSON files, vanilla JavaScript, CSS, Lucide icon stylesheet CDN.

**Spec:** `docs/superpowers/specs/2026-11-05-tezal-small-shop-ux-design.md`

## Global Constraints

- Analytics stays on the Dashboard and is not a separate navigation item.
- New orders use the label `New order`; do not describe the workflow as an Instagram order.
- Supported channels are `Instagram`, `WhatsApp`, and `Other`.
- Existing orders without a channel render as `Other`.
- Keep local JSON storage and existing bill image generation.
- Do not add a frontend framework, chart dependency, authentication, or cloud service.

## Review Focus

- Existing orders without `channel` must render and filter as `Other`.
- A new order must persist the selected channel without changing totals or stock deduction.
- Dashboard analytics must remain useful when there are no orders or products.
- Small viewport layouts must keep the primary order and inventory actions usable.
- Customer-facing bill output must not expose internal cost/profit fields.

---

### Task 1: Add backward-compatible order channels and analytics data

**Files:**
- Modify: `storage.py`
- Modify: `main.py`
- Modify: `test_app.py`

**Interfaces:**
- `storage.create_order(..., channel)` persists `channel`.
- `storage.get_order_channel(order)` returns `order.get("channel", "Other")` behavior inline or via equivalent helper.
- `storage.get_dashboard_stats()` returns dashboard-safe store/channel aggregates.
- `main.create_order_action` accepts `channel` from the form and passes it to storage.

- [ ] **Step 1: Add failing tests** for selected channel persistence, legacy order fallback, and dashboard channel summary.
- [ ] **Step 2: Run `pytest -q test_app.py` and verify the new assertions fail because channel is not persisted/returned yet.
- [ ] **Step 3: Implement the smallest storage and route changes** to persist supported channels and normalize missing values to `Other` when reading/aggregating.
- [ ] **Step 4: Run `pytest -q test_app.py` and verify the full existing workflow passes.

### Task 2: Rebuild the shared shell and visual system

**Files:**
- Modify: `templates/base.html`
- Modify: `static/css/style.css`

**Interfaces:**
- Templates use shared `page-header`, `section-heading`, `metric-card`, `badge`, `icon`, and responsive layout classes.
- Navigation labels are `Overview`, `Orders`, `Inventory`, and `New order`.

- [ ] **Step 1: Add template-level assertions** for the new navigation labels and absence of `New Instagram Order`.
- [ ] **Step 2: Run the relevant template tests and verify the new labels fail.
- [ ] **Step 3: Implement the pink/black shell, Lucide icon stylesheet, responsive nav, accessible buttons, flash messages, and shared layout classes.
- [ ] **Step 4: Run the full test suite and verify all existing routes still render.

### Task 3: Make the Dashboard the useful analytics home

**Files:**
- Modify: `templates/dashboard.html`
- Modify: `main.py` only if additional context is needed
- Modify: `static/css/style.css` for dashboard-specific layout

**Interfaces:**
- Dashboard renders current-month metrics, store mix, channel mix, low-stock attention, and recent orders.
- Dashboard primary action is `New order`; secondary action is `View inventory`.

- [ ] **Step 1: Add route/template assertions** for today revenue/profit/orders, store/channel mix, and low-stock copy.
- [ ] **Step 2: Run tests and verify the new assertions fail against the old dashboard.
- [ ] **Step 3: Implement the compact dashboard layout with empty states and simple CSS bars for store/channel mix.
- [ ] **Step 4: Run the full test suite and verify the dashboard works with seeded and empty data.

### Task 4: Separate and polish Orders/Sales

**Files:**
- Modify: `templates/orders.html`
- Modify: `templates/new_order.html`
- Modify: `templates/bill_preview.html`
- Modify: `static/js/order.js`
- Modify: `static/js/validation.js` only if copy/validation needs updating
- Modify: `static/css/style.css`

**Interfaces:**
- Orders page supports store, channel, and date filters and shows filter-scoped orders, revenue, profit, and average order value.
- New order flow includes store and channel choice before customer details.
- Order details show store and channel while preserving bill download and internal profit breakdown.

- [ ] **Step 1: Add failing route assertions** for channel filter, channel selector, and New order copy.
- [ ] **Step 2: Run tests and verify the assertions fail.
- [ ] **Step 3: Implement the focused order-entry layout, channel badges/filter, compact table, clearer summary card, and updated bill detail metadata.
- [ ] **Step 4: Run the full test suite and verify creation, filtering, bill preview, and stock restoration.

### Task 5: Separate and polish Inventory

**Files:**
- Modify: `templates/inventory.html`
- Modify: `templates/edit_product.html`
- Modify: `static/css/style.css`
- Modify: `static/js/order.js` if inventory search behavior needs cleanup

**Interfaces:**
- Inventory page shows inventory-only summary cards, search, stock status, margin, and clear add/edit actions.
- Product add/edit remains compatible with existing validation and storage routes.

- [ ] **Step 1: Add failing template assertions** for inventory-only headings, stock summary labels, and no order-language leakage.
- [ ] **Step 2: Run tests and verify the new assertions fail.
- [ ] **Step 3: Implement the inventory workspace with a clear add-product form, searchable table, stock status badges, and calm empty state.
- [ ] **Step 4: Run the full test suite and verify add/edit/delete/search behavior.

### Task 6: Documentation and final verification

**Files:**
- Modify: `README.md`
- Modify: `app.py` and `main.py` startup copy if needed

- [ ] **Step 1: Search for stale `Instagram Order` UI copy and update it to `New order` or channel-specific wording only where appropriate.
- [ ] **Step 2: Run `pytest -q`.
- [ ] **Step 3: Run a local smoke check against dashboard, orders, new order, inventory, and a channel-filtered orders request.
- [ ] **Step 4: Review the changed templates/CSS for mobile overflow, missing labels, and accidental emoji-heavy copy.
