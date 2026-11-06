# Tezal Small-Shop Workspace UX Design

## Intent

Make Tezal's local inventory app feel like a calm daily workspace for two small shops. The app should help her answer three questions quickly: what sold, what needs attention, and what is in stock.

The redesign keeps the existing FastAPI, Jinja, JSON storage, and bill-image workflow. It improves the information architecture, visual hierarchy, copy, and order data model without introducing a frontend build system or a complex database.

## Goals

- Separate Orders/Sales and Inventory as distinct primary workflows.
- Make creating a new order fast and understandable: store, channel, customer, items, payment, review, save.
- Replace "Instagram order" language with "New order" and store the channel per order.
- Use a restrained pink-and-black visual system with clean iconography and accessible states.
- Show small-business analytics that support daily decisions: revenue, profit, order count, average order value, store/channel mix, and stock alerts.
- Preserve existing orders and products; older orders without a channel display as `Other`.
- Keep the app local, lightweight, and easy to run on Tezal's laptop.

## Non-goals

- No authentication, cloud sync, multi-user permissions, or accounting system.
- No delivery tracking, customer CRM, product photos, variants, or barcode scanning.
- No charts library or frontend framework; analytics can use compact summary cards and simple visual bars where useful.
- No migration away from JSON files.

## Anti-goals

- Do not make every screen look like a dashboard.
- Do not hide core actions behind menus or modal-heavy flows.
- Do not use emojis as the primary icon system or add decorative animation.
- Do not expose internal cost/profit details in the customer-facing bill image.

## Approaches considered

1. **Focused existing-app redesign — chosen.** Keep FastAPI/Jinja/JSON, add a small icon library through an external stylesheet link with a no-icon fallback, add the `channel` field, and rebuild the main templates/CSS around distinct workspaces. Lowest risk and best fit for a local two-shop app.
2. **Component-based frontend rebuild.** Would allow more custom interaction patterns but adds build tooling, dependency maintenance, and complexity that does not improve the core workflow enough.
3. **Backend-first reporting expansion.** Would add more metrics and filtering before improving the screens. Rejected because the current problem is clarity and flow, not lack of data.

## Information architecture

- **Overview** (`/`): today-first snapshot, key actions, low-stock attention, recent orders.
- **Orders** (`/orders`): order history, filters, sales/profit summary, bill access, and a prominent `New order` action.
- **Inventory** (`/inventory`): stock list, add product action, search, low-stock status, margin, edit/restock.
- **New order** (`/orders/new`): focused order-entry flow with store and channel selection at the top.

## Order data change

Add `channel` to new order form submission and persisted order records. Supported values are `Instagram`, `WhatsApp`, and `Other`. Existing records without this field render as `Other`; no destructive data migration is required.

The order history should show channel as a compact badge and allow filtering by channel in addition to store and date. The order detail page should show both store and channel in its metadata.

## Visual direction

- Background: warm near-white; surfaces: white; primary ink: near-black.
- Accent: a confident berry-pink used for primary actions, active states, and key highlights.
- Supporting colors: muted rose for warnings, green for positive profit/stock health, neutral gray for secondary content.
- Rounded corners and shadows should be subtle; typography and spacing do most of the work.
- Use Lucide icons through a stylesheet CDN link in the base template, with `aria-hidden` icons paired with visible labels.
- Avoid inline style sprawl by adding reusable layout, page-header, metric, filter, badge, empty-state, and order-form classes.

## Analytics

Dashboard metrics for the current English calendar month:

- This month's revenue
- This month's profit
- This month's orders
- Products needing attention (low or out of stock)

Dashboard supporting views:

- Recent orders with store, channel, customer, total, and profit.
- Store comparison showing order count, revenue, and profit.
- Channel mix showing order count by Instagram, WhatsApp, and Other.

Orders page metrics should reflect the current filter view: orders, revenue, profit, and average order value. Inventory should show total products, total units, low-stock count, and out-of-stock count.

## UX details

- `New order` is the only order-creation label across navigation, dashboard, orders, and documentation.
- Channel is selected as a small, clear choice group; it is not inferred from customer contact text or notes.
- Product rows use a readable product selector, quantity, selling price, and line total; cost remains visually secondary because it is internal.
- The order summary stays visible on desktop and becomes a normal section on small screens.
- Empty states explain the next action in one sentence and provide one button.
- Dangerous actions remain explicit and confirm before deleting an order or product.

## Builder decisions

- Use a simple CSS bar treatment for channel/store mix instead of adding a chart dependency.
- Keep the two existing store names and selection behavior.
- Keep current payment options and bill image generation.
- Use icon names from Lucide (`layout-dashboard`, `shopping-bag`, `boxes`, `plus`, `search`, `download`, `trash-2`, `pencil`, `message-circle`, `instagram`) with text labels for clarity.
