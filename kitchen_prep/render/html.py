"""Server-rendered bilingual dashboard for the latest kitchen plan."""
from __future__ import annotations

from html import escape

from ..data_access import menu as menu_da


def _run_status(plan: dict, language: str) -> tuple[str, bool]:
    sources = {plan["forecast"]["forecast_source"], plan.get("briefing_source", "")}
    degraded = "deterministic_fallback" in sources
    if degraded:
        return ("DEGRADED" if language == "en" else "DEGRADERT"), True
    return "OPERATIONAL" if language == "en" else "OPERATIV", False


def _human_id(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _dish_name(dish_id: str) -> str:
    return str(menu_da.menu_by_id().get(dish_id, {}).get("name") or _human_id(dish_id))


def _item_name(item_id: str) -> str:
    return _human_id(item_id)


def _unit(unit: str, language: str) -> str:
    if unit == "stk":
        return "pcs" if language == "en" else "stk"
    return unit


def _reasoning_text(reasoning: str, language: str, fallback: bool) -> str:
    if language == "no" and fallback:
        return "Deterministisk baseline basert på de siste tilsvarende ukedagene, normalisert per gjest."
    return reasoning


_STYLE = """
:root {
  color-scheme: light;
  --ink: #17211b; --muted: #66736b; --line: #dfe7e1; --paper: #fff;
  --canvas: #f3f6f3; --brand: #174c35; --brand-soft: #e2efe8;
  --good: #14733c; --warn: #a95508; --danger: #a42929; --shadow: 0 10px 30px #173a2520;
}
* { box-sizing: border-box; }
body { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 0; background: var(--canvas); color: var(--ink); line-height: 1.45; }
.shell { width: min(1080px, calc(100% - 2rem)); margin: 0 auto; padding: 1.25rem 0 3rem; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
.brand { display: flex; align-items: center; gap: .7rem; font-weight: 800; letter-spacing: -.02em; }
.mark { display: grid; place-items: center; width: 2.3rem; height: 2.3rem; border-radius: .7rem;
  color: white; background: var(--brand); font-size: 1.2rem; }
.language { color: var(--brand); border: 1px solid #aac5b5; border-radius: 999px; padding: .38rem .75rem;
  text-decoration: none; font-size: .82rem; font-weight: 700; background: white; }
.hero { color: white; background: linear-gradient(135deg, #123d2c, #256a49); border-radius: 1.25rem;
  padding: clamp(1.25rem, 4vw, 2.2rem); box-shadow: var(--shadow); }
.hero-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
.eyebrow { margin: 0 0 .25rem; opacity: .78; text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; font-weight: 800; }
h1 { margin: 0; font-size: clamp(1.7rem, 5vw, 2.7rem); line-height: 1.1; letter-spacing: -.04em; }
.hero p { margin: .55rem 0 0; color: #d9e9df; }
.status { display: inline-flex; align-items: center; gap: .45rem; border-radius: 999px; padding: .45rem .75rem;
  background: #ffffff18; border: 1px solid #ffffff3d; font-size: .78rem; font-weight: 800; letter-spacing: .04em; }
.dot { width: .55rem; height: .55rem; border-radius: 50%; background: #62db88; box-shadow: 0 0 0 4px #62db8825; }
.status.degraded .dot { background: #ffb55f; box-shadow: 0 0 0 4px #ffb55f25; }
.cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .75rem; margin: 1rem 0; }
.card, .panel { background: var(--paper); border: 1px solid var(--line); border-radius: 1rem; box-shadow: 0 3px 14px #173a2508; }
.card { padding: 1rem; }
.card .label { color: var(--muted); font-size: .72rem; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; }
.card .value { display: block; margin-top: .15rem; font-size: 1.55rem; line-height: 1.15; font-weight: 850; letter-spacing: -.04em; }
.grid { display: grid; grid-template-columns: 1.35fr .9fr; gap: 1rem; align-items: start; }
.stack { display: grid; gap: 1rem; }
.panel { overflow: hidden; }
.panel-head { padding: 1rem 1.1rem .75rem; border-bottom: 1px solid var(--line); }
.panel-head h2 { margin: 0; font-size: 1rem; letter-spacing: -.01em; }
.panel-head p { margin: .15rem 0 0; color: var(--muted); font-size: .8rem; }
.rows { list-style: none; padding: 0; margin: 0; }
.row { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: .8rem; padding: .85rem 1.1rem; border-bottom: 1px solid var(--line); }
.row:last-child { border-bottom: 0; }
.rank { display: grid; place-items: center; width: 1.8rem; height: 1.8rem; border-radius: .55rem; color: var(--brand);
  background: var(--brand-soft); font-size: .76rem; font-weight: 850; }
.name { font-weight: 750; }
.sub { color: var(--muted); font-size: .78rem; margin-top: .08rem; }
.qty { font-weight: 850; white-space: nowrap; }
.alert { border-left: 4px solid var(--warn); }
.danger { border-left: 4px solid var(--danger); }
.empty { color: var(--muted); padding: 1rem 1.1rem; margin: 0; font-style: italic; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .83rem; }
th, td { text-align: left; padding: .72rem .8rem; border-bottom: 1px solid var(--line); white-space: nowrap; }
th { color: var(--muted); font-size: .68rem; text-transform: uppercase; letter-spacing: .06em; }
tr:last-child td { border-bottom: 0; }
.source { display: flex; justify-content: space-between; gap: .75rem; padding: .75rem 1.1rem; border-bottom: 1px solid var(--line); font-size: .8rem; }
.source:last-child { border-bottom: 0; }
.source span:first-child { color: var(--muted); }
.source strong { text-align: right; }
.driver-list { display: flex; flex-wrap: wrap; gap: .4rem; padding: 1rem 1.1rem; }
.chip { display: inline-block; border-radius: 999px; padding: .28rem .55rem; background: #edf1ee; color: #425148; font-size: .72rem; }
.forecast-row { padding: .8rem 1.1rem; border-bottom: 1px solid var(--line); }
.forecast-row:last-child { border-bottom: 0; }
.forecast-top { display: flex; justify-content: space-between; gap: .75rem; }
.reason { color: var(--muted); font-size: .76rem; margin-top: .18rem; }
.confidence { color: var(--brand); font-size: .68rem; font-weight: 850; text-transform: uppercase; }
.footer { color: var(--muted); text-align: center; font-size: .72rem; margin-top: 1rem; }
@media (max-width: 780px) { .cards { grid-template-columns: repeat(2, 1fr); } .grid { grid-template-columns: 1fr; } }
@media (max-width: 430px) { .shell { width: min(100% - 1rem, 1080px); } .hero { border-radius: 1rem; }
  .cards { gap: .5rem; } .card { padding: .8rem; } .row { padding: .78rem .85rem; } }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark; --ink: #e9f0eb; --muted: #a8b5ad;
  --line: #33453a; --paper: #17231c; --canvas: #101711; --brand-soft: #264737; --shadow: none; }
  .language { background: #17231c; border-color: #496b58; color: #a9dfbf; } .chip { background: #28372e; color: #c4d0c8; } }
""".strip()


def _empty(message: str) -> str:
    return f'<p class="empty">{escape(message)}</p>'


def render_home(
    plan: dict | None,
    language: str = "no",
    available_plans: list[dict] | None = None,
) -> str:
    language = "en" if language == "en" else "no"
    en = language == "en"
    switch = (
        '<a class="language" href="?lang=no" lang="no">Norsk</a>'
        if en else '<a class="language" href="?lang=en" lang="en">English</a>'
    )
    brand = '<div class="brand"><span class="mark">K</span><span>Kitchen Prep Taskmaster</span></div>'

    if plan is None:
        message = "No plan has been published yet." if en else "Ingen plan er publisert ennå."
        return f"""<!doctype html><html lang="{language}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Kitchen Prep Taskmaster</title>
<style>{_STYLE}</style></head><body><main class="shell"><nav class="topbar">{brand}{switch}</nav>
<section class="panel">{_empty(message)}</section></main></body></html>"""

    status, degraded = _run_status(plan, language)
    prep = sorted(plan.get("prep_tasks", []), key=lambda task: task["priority"])
    shortfalls = plan.get("prep_shortfalls", [])
    orders = plan.get("replenishment_orders", [])
    waste = plan.get("waste_flagged", [])
    forecast = plan.get("forecast", {})

    prep_rows = "".join(
        f'<li class="row"><span class="rank">{task["priority"]}</span><div><div class="name">{escape(_dish_name(task["dish_id"]))}</div>'
        f'<div class="sub">{escape(str(task["prep_minutes"]))} min · {escape(task["dish_id"])}</div></div>'
        f'<span class="qty">{escape(str(task["qty"]))} {"pcs" if en else "stk"}</span></li>'
        for task in prep
    )
    prep_block = f'<ul class="rows">{prep_rows}</ul>' if prep else _empty("No prep tasks." if en else "Ingen prep-oppgaver.")

    short_rows = "".join(
        f'<li class="row alert"><span class="rank">!</span><div><div class="name">{escape(_item_name(item["item_id"]))}</div>'
        f'<div class="sub">{("Available" if en else "Tilgjengelig")}: {escape(str(item["available"]))} · '
        f'{("Required" if en else "Behov")}: {escape(str(item["required"]))}</div></div>'
        f'<span class="qty">−{escape(str(item["shortfall"]))}</span></li>'
        for item in shortfalls
    )
    short_block = f'<ul class="rows">{short_rows}</ul>' if shortfalls else _empty("No shortfalls today." if en else "Ingen mangler i dag.")

    order_rows = "".join(
        f'<tr><td><strong>{escape(_item_name(order["item_id"]))}</strong></td>'
        f'<td>{escape(str(order["order_qty"]))} {escape(_unit(order["unit"], language))}</td>'
        f'<td>{escape(order["supplier"])}</td><td>{escape(order["delivery_date"])}</td></tr>'
        for order in orders
    )
    order_block = (
        f'<div class="table-wrap"><table><thead><tr><th>{"Item" if en else "Vare"}</th><th>{"Order" if en else "Bestill"}</th>'
        f'<th>{"Supplier" if en else "Leverandør"}</th><th>{"Delivery" if en else "Levering"}</th></tr></thead><tbody>{order_rows}</tbody></table></div>'
        if orders else _empty("No replenishment orders." if en else "Ingen bestillinger.")
    )

    waste_rows = "".join(
        f'<li class="row danger"><span class="rank">×</span><div><div class="name">{escape(_item_name(item["item_id"]))}</div>'
        f'<div class="sub">{escape(item["batch_id"])} · {("Expired" if en else "Utløpt")} {escape(item["expiry_date"])}</div></div>'
        f'<span class="qty">{escape(str(item["qty"]))}</span></li>' for item in waste
    )
    waste_block = f'<ul class="rows">{waste_rows}</ul>' if waste else _empty("No expired waste." if en else "Ingen utgått svinn.")

    drivers = forecast.get("drivers", [])
    driver_block = "".join(f'<span class="chip">{escape(_human_id(str(driver)))}</span>' for driver in drivers)
    forecast_rows = "".join(
        f'<div class="forecast-row"><div class="forecast-top"><span class="name">{escape(_dish_name(item["dish_id"]))}</span>'
        f'<span class="qty">{escape(str(item["expected_qty"]))}</span></div>'
        f'<div class="confidence">{escape(str(item.get("confidence", "medium")))}</div>'
        f'<div class="reason">{escape(_reasoning_text(str(item.get("reasoning", "")), language, forecast.get("forecast_source") == "deterministic_fallback"))}</div></div>'
        for item in forecast.get("dishes", [])
    )

    status_class = "status degraded" if degraded else "status"
    forecast_note = plan.get("forecast_note", "")
    history_items = []
    for historic in available_plans or []:
        historic_date = str(historic.get("date", ""))
        if not historic_date:
            continue
        selected = historic_date == str(plan.get("date"))
        href = f"?lang={language}&amp;date={escape(historic_date)}"
        label = f'{historic_date} · {historic.get("expected_covers", "—")} {"guests" if en else "gjester"}'
        history_items.append(
            f'<a class="chip" href="{href}"{(" aria-current=\"page\"" if selected else "")}>{escape(label)}</a>'
        )
    history_block = "".join(history_items)
    return f"""<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kitchen Prep — {escape(plan['date'])}</title><style>{_STYLE}</style></head><body><main class="shell">
<nav class="topbar">{brand}{switch}</nav>
<header class="hero"><div class="hero-row"><div><p class="eyebrow">{"Daily operations plan" if en else "Dagens driftsplan"}</p>
<h1>{"Ready for service" if en else "Klar for service"}</h1><p>{escape(plan['date'])} · {escape(str(plan.get('generated_at', '')))}</p></div>
<span class="{status_class}"><span class="dot"></span>{escape(status)}</span></div></header>

<section class="cards" aria-label="Key metrics">
<div class="card"><span class="label">{"Expected guests" if en else "Forventede gjester"}</span><span class="value">{escape(str(plan['expected_covers']))}</span></div>
<div class="card"><span class="label">{"Prep tasks" if en else "Prep-oppgaver"}</span><span class="value">{len(prep)}</span></div>
<div class="card"><span class="label">{"Shortfalls" if en else "Mangler"}</span><span class="value">{len(shortfalls)}</span></div>
<div class="card"><span class="label">{"Orders" if en else "Bestillinger"}</span><span class="value">{len(orders)}</span></div>
</section>

<div class="grid"><div class="stack">
{f'<section class="panel"><header class="panel-head"><h2>{"Plan history" if en else "Planhistorikk"}</h2><p>{"Read-only Firestore plans" if en else "Skrivebeskyttede Firestore-planer"}</p></header><div class="driver-list">{history_block}</div></section>' if history_block else ''}
<section class="panel"><header class="panel-head"><h2>{"Prioritized prep" if en else "Prioritert prep"}</h2><p>{"What the kitchen should start first" if en else "Det kjøkkenet bør starte med først"}</p></header>{prep_block}</section>
<section class="panel"><header class="panel-head"><h2>{"Today’s shortfalls" if en else "Mangler i dag"}</h2><p>{"Required for service, separate from replenishment" if en else "Behov til service, adskilt fra bestilling"}</p></header>{short_block}</section>
<section class="panel"><header class="panel-head"><h2>{"Replenishment orders" if en else "Bestillinger til par"}</h2><p>{"Calculated from inventory remaining after today’s consumption" if en else "Beregnet fra lager etter dagens forbruk"}</p></header>{order_block}</section>
</div><aside class="stack">
<section class="panel"><header class="panel-head"><h2>{"Run integrity" if en else "Kjøringsintegritet"}</h2><p>{"Model paths and audit status" if en else "Modellbaner og revisjonsstatus"}</p></header>
<div class="source"><span>{"Forecast" if en else "Prognose"}</span><strong>{escape(str(forecast.get('forecast_source', '')))}</strong></div>
<div class="source"><span>{"Briefing" if en else "Briefing"}</span><strong>{escape(str(plan.get('briefing_source', '')))}</strong></div>
<div class="source"><span>{"Inventory" if en else "Lager"}</span><strong>{escape(str(plan.get('inventory_basis', 'seed_inventory')))}</strong></div>
<div class="source"><span>{"Diagnostic" if en else "Diagnostikk"}</span><strong>{escape(str(forecast_note or '—'))}</strong></div></section>
<section class="panel"><header class="panel-head"><h2>{"Forecast drivers" if en else "Prognosedrivere"}</h2><p>{"Signals used by the validated demand proposal" if en else "Signaler brukt i validert etterspørselsforslag"}</p></header><div class="driver-list">{driver_block or '<span class="chip">—</span>'}</div>{forecast_rows}</section>
<section class="panel"><header class="panel-head"><h2>{"Expired waste" if en else "Utgått svinn"}</h2><p>{"Removed before FEFO consumption" if en else "Fjernet før FEFO-forbruk"}</p></header>{waste_block}</section>
</aside></div>
<footer class="footer">{"Gemini judgment · deterministic arithmetic · Firestore audit trail" if en else "Gemini-vurdering · deterministiske beregninger · Firestore-spor"}</footer>
</main></body></html>"""
