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
  --ink: #14201a; --muted: #5c6b62; --line: #dde6e0; --paper: #ffffff;
  --canvas: #eef3ef; --brand: #16513a; --brand-2: #1f6a49; --brand-soft: #e4f0ea;
  --good: #147a3e; --warn: #9a5406; --danger: #a32828;
  --radius: 16px; --radius-sm: 11px;
  --shadow-sm: 0 1px 2px rgba(20,50,35,.06), 0 1px 1px rgba(20,50,35,.04);
  --shadow: 0 10px 34px rgba(20,50,35,.12);
  --ring: 0 0 0 3px #1f6a4940;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 0; background: var(--canvas); color: var(--ink); line-height: 1.5;
  -webkit-font-smoothing: antialiased; }
.shell { width: min(1080px, calc(100% - 2rem)); margin: 0 auto; padding: 1.25rem 0 3rem; }
a { color: inherit; }
:focus-visible { outline: none; box-shadow: var(--ring); border-radius: 8px; }

.topbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.15rem; }
.brand { display: flex; align-items: center; gap: .7rem; font-weight: 800; letter-spacing: -.02em; }
.mark { display: grid; place-items: center; width: 2.35rem; height: 2.35rem; border-radius: .75rem;
  color: white; background: linear-gradient(150deg, var(--brand-2), var(--brand)); font-size: 1.2rem;
  box-shadow: var(--shadow-sm); }
.language { color: var(--brand); border: 1px solid #b5cec0; border-radius: 999px; padding: .42rem .85rem;
  text-decoration: none; font-size: .82rem; font-weight: 700; background: white; transition: background .15s, border-color .15s; }
.language:hover { background: var(--brand-soft); border-color: #98bfa9; }

.hero { position: relative; min-height: 25rem; display: flex; align-items: flex-end; color: white;
  background: #103724 url('/assets/food-hero.webp') center/cover no-repeat;
  border-radius: 20px; padding: clamp(1.35rem, 4vw, 2.35rem); box-shadow: var(--shadow); overflow: hidden; }
.hero::before { content: ""; position: absolute; inset: 0; background:
  linear-gradient(90deg, rgba(7,29,19,.96) 0%, rgba(9,38,25,.86) 38%, rgba(9,38,25,.28) 70%, rgba(9,38,25,.08) 100%); pointer-events: none; }
.hero::after { content: ""; position: absolute; inset: 0; background:
  linear-gradient(0deg, rgba(3,18,11,.6), transparent 45%); pointer-events: none; }
.hero-row { position: relative; display: flex; justify-content: space-between; align-items: flex-start;
  gap: 1rem; flex-wrap: wrap; width: 100%; z-index: 1; }
.hero-copy { max-width: 35rem; }
.hero-kicker { display: inline-block; margin-top: .7rem; color: #b9e6c6; font-size: .78rem; font-weight: 850;
  text-transform: uppercase; letter-spacing: .08em; }
.eyebrow { margin: 0 0 .35rem; opacity: .82; text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 800; }
h1 { margin: 0; font-size: clamp(1.7rem, 5vw, 2.7rem); line-height: 1.08; letter-spacing: -.035em; }
.hero p { margin: .6rem 0 0; color: #d7e8de; font-variant-numeric: tabular-nums; }
.status { display: inline-flex; align-items: center; gap: .5rem; border-radius: 999px; padding: .5rem .85rem;
  background: #ffffff1c; border: 1px solid #ffffff45; font-size: .76rem; font-weight: 800; letter-spacing: .05em; }
.dot { width: .58rem; height: .58rem; border-radius: 50%; background: #6fe295; box-shadow: 0 0 0 4px #6fe29528; }
.status.degraded { background: #ffb55f1f; border-color: #ffcf9a66; }
.status.degraded .dot { background: #ffc178; box-shadow: 0 0 0 4px #ffc17826; }
.hero-actions { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.15rem; }
.hero-link { display: inline-flex; align-items: center; gap: .4rem; padding: .55rem .8rem; border-radius: 999px;
  color: white; background: #ffffff17; border: 1px solid #ffffff42; text-decoration: none; font-size: .76rem;
  font-weight: 800; backdrop-filter: blur(8px); transition: background .15s, border-color .15s, transform .15s; }
.hero-link:hover { background: #ffffff29; border-color: #ffffff70; transform: translateY(-1px); }
.value-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin: 1.1rem 0; }
.value-card { display: grid; grid-template-columns: auto 1fr; gap: .75rem; align-items: start; padding: 1rem 1.05rem;
  background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow-sm); }
.value-icon { display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: .65rem;
  color: var(--brand); background: var(--brand-soft); font-weight: 900; }
.value-card strong { display: block; font-size: .85rem; }
.value-card span:last-child { display: block; margin-top: .12rem; color: var(--muted); font-size: .74rem; }

.cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; margin: 1.1rem 0; }
.card, .panel { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); }
.card { padding: 1.05rem 1.1rem; box-shadow: var(--shadow-sm); position: relative;
  transition: transform .12s ease, box-shadow .12s ease; }
.card:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
.card .label { color: var(--muted); font-size: .72rem; font-weight: 800; text-transform: uppercase; letter-spacing: .07em; }
.card .value { display: block; margin-top: .2rem; font-size: 1.7rem; line-height: 1.1; font-weight: 850;
  letter-spacing: -.03em; font-variant-numeric: tabular-nums; }
.card--alert { border-color: #e7c3c3; }
.card--alert::before { content: ""; position: absolute; left: 0; top: .9rem; bottom: .9rem; width: 3px;
  border-radius: 3px; background: var(--danger); }
.card--alert .value { color: var(--danger); }

.run-flow { margin: 1.1rem 0; }
.flow-list { list-style: none; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); margin: 0; padding: 0; }
.flow-step { position: relative; min-width: 0; padding: 1rem .9rem; border-right: 1px solid var(--line); }
.flow-step:last-child { border-right: 0; }
.flow-top { display: flex; align-items: center; gap: .45rem; margin-bottom: .4rem; }
.flow-number { display: grid; place-items: center; flex: 0 0 auto; width: 1.45rem; height: 1.45rem;
  border-radius: 50%; color: white; background: var(--brand); font-size: .68rem; font-weight: 850; }
.flow-label { color: var(--muted); font-size: .65rem; font-weight: 850; text-transform: uppercase; letter-spacing: .06em; }
.flow-value { display: block; font-size: .82rem; font-weight: 800; overflow-wrap: anywhere; }
.flow-detail { display: block; margin-top: .18rem; color: var(--muted); font-size: .7rem; overflow-wrap: anywhere; }
.flow-step--fallback .flow-number { background: var(--warn); }
.grid { display: grid; grid-template-columns: 1.35fr .9fr; gap: 1rem; align-items: start; }
.stack { display: grid; gap: 1rem; }
.panel { overflow: hidden; box-shadow: var(--shadow-sm); }
.panel-head { padding: 1.05rem 1.15rem .8rem; border-bottom: 1px solid var(--line); }
.panel-head h2 { margin: 0; font-size: 1rem; letter-spacing: -.01em; }
.panel-head p { margin: .2rem 0 0; color: var(--muted); font-size: .8rem; }
.rows { list-style: none; padding: 0; margin: 0; }
.row { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: .85rem;
  padding: .8rem 1.15rem; border-bottom: 1px solid var(--line); transition: background .12s; }
.row:last-child { border-bottom: 0; }
.row:hover { background: #f6faf7; }
.rank { display: grid; place-items: center; width: 1.85rem; height: 1.85rem; border-radius: .6rem; color: var(--brand);
  background: var(--brand-soft); font-size: .78rem; font-weight: 850; font-variant-numeric: tabular-nums; }
.name { font-weight: 750; }
.sub { color: var(--muted); font-size: .78rem; margin-top: .1rem; font-variant-numeric: tabular-nums; }
.qty { font-weight: 850; white-space: nowrap; font-variant-numeric: tabular-nums; }
.alert .rank { color: var(--warn); background: #f7ecdd; }
.alert .qty { color: var(--warn); }
.danger .rank { color: var(--danger); background: #f6dede; }
.empty { color: var(--muted); padding: 1.05rem 1.15rem; margin: 0; font-style: italic; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .84rem; }
th, td { text-align: left; padding: .74rem .85rem; border-bottom: 1px solid var(--line); white-space: nowrap; }
td { font-variant-numeric: tabular-nums; }
td:first-child { font-variant-numeric: normal; }
th { color: var(--muted); font-size: .68rem; text-transform: uppercase; letter-spacing: .06em; }
tbody tr:hover td { background: #f6faf7; }
tr:last-child td { border-bottom: 0; }
.source { display: flex; justify-content: space-between; gap: .75rem; padding: .78rem 1.15rem;
  border-bottom: 1px solid var(--line); font-size: .8rem; }
.source:last-child { border-bottom: 0; }
.source span:first-child { color: var(--muted); }
.source strong { text-align: right; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.driver-list { display: flex; flex-wrap: wrap; gap: .45rem; padding: 1.05rem 1.15rem; }
.chip { display: inline-block; border-radius: 999px; padding: .3rem .6rem; background: #edf2ee; color: #3f5147;
  font-size: .72rem; text-decoration: none; transition: background .12s; }
a.chip:hover { background: var(--brand-soft); }
a.chip[aria-current="page"] { background: var(--brand); color: #fff; }
.forecast-row { padding: .82rem 1.15rem; border-bottom: 1px solid var(--line); }
.forecast-row:last-child { border-bottom: 0; }
.forecast-top { display: flex; justify-content: space-between; gap: .75rem; }
.reason { color: var(--muted); font-size: .76rem; margin-top: .2rem; }
.confidence { color: var(--brand); font-size: .68rem; font-weight: 850; text-transform: uppercase; letter-spacing: .04em; margin-top: .12rem; }
.briefing-summary { margin: 0; padding: 1rem 1.15rem; border-bottom: 1px solid var(--line); }
.action-badge { display: inline-block; margin-top: .35rem; border-radius: 999px; padding: .2rem .5rem;
  color: var(--warn); background: #f7ecdd; font-size: .65rem; font-weight: 850; text-transform: uppercase; letter-spacing: .04em; }
.warning-list { margin: 0; padding: .85rem 1.15rem .95rem 2.2rem; color: var(--warn); font-size: .78rem; }
.warning-list li + li { margin-top: .35rem; }
.footer { color: var(--muted); text-align: center; font-size: .72rem; margin-top: 1.25rem; }
@media (max-width: 780px) { .hero { min-height: 29rem; background-position: 62% center; }
  .hero::before { background: linear-gradient(90deg, rgba(7,29,19,.95), rgba(7,29,19,.72)); }
  .value-strip { grid-template-columns: 1fr; } .cards { grid-template-columns: repeat(2, 1fr); } .grid { grid-template-columns: 1fr; }
  .flow-list { grid-template-columns: 1fr; } .flow-step { border-right: 0; border-bottom: 1px solid var(--line); }
  .flow-step:last-child { border-bottom: 0; } }
@media (max-width: 430px) { .shell { width: min(100% - 1rem, 1080px); } .hero { border-radius: 16px; }
  .cards { gap: .55rem; } .card { padding: .85rem .9rem; } .card .value { font-size: 1.5rem; }
  .row { padding: .74rem .9rem; } }
@media (prefers-color-scheme: dark) { :root { color-scheme: dark; --ink: #e9f0eb; --muted: #a4b3ab;
  --line: #2f4239; --paper: #16221b; --canvas: #0e150f; --brand-soft: #21402f; --brand: #6fbf93;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.4); --shadow: 0 10px 34px rgba(0,0,0,.5); }
  .language { background: #16221b; border-color: #3f5f4d; color: #a9dfbf; }
  .chip { background: #243228; color: #c4d0c8; } a.chip:hover { background: #2c4a38; }
  .row:hover, tbody tr:hover td { background: #1b2a21; }
  .card--alert { border-color: #5a2f2f; } .card--alert .value { color: #f0a1a1; }
  .alert .rank, .action-badge { background: #3a2f1f; } .danger .rank { background: #3a2323; } }
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

    briefing = plan.get("briefing", {})
    briefing_summary = str(briefing.get("summary", "")).strip()
    action_rows = "".join(
        f'<li class="row alert"><span class="rank">!</span><div><div class="name">{escape(_item_name(action["item_id"]))}</div>'
        f'<div class="reason">{escape(str(action.get("recommended_action", "")))}</div>'
        f'{("<span class=\"action-badge\">" + ("Human approval required" if en else "Krever menneskelig godkjenning") + "</span>") if action.get("requires_human_approval") else ""}'
        f'</div></li>'
        for action in briefing.get("shortfall_actions", [])
        if action.get("item_id")
    )
    warning_items = "".join(
        f'<li>{escape(str(warning))}</li>' for warning in briefing.get("warnings", []) if str(warning).strip()
    )
    briefing_content = (
        (f'<p class="briefing-summary">{escape(briefing_summary)}</p>' if briefing_summary else "")
        + (f'<ul class="rows">{action_rows}</ul>' if action_rows else "")
        + (f'<ul class="warning-list">{warning_items}</ul>' if warning_items else "")
    ) or _empty("No agent briefing." if en else "Ingen agentbriefing.")

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
    forecast_source = str(forecast.get("forecast_source", "unknown"))
    briefing_source = str(plan.get("briefing_source", "unknown"))
    validation_fallback = forecast_source == "deterministic_fallback"
    validation_value = ("Fallback activated" if en else "Fallback aktivert") if validation_fallback else ("Proposal accepted" if en else "Forslag godkjent")
    fefo_count = len(plan.get("fefo_consumption", []))
    covers_source = str(plan.get("covers_source", "expected_covers"))
    planning_basis = str(plan.get("planning_basis", "today_consumption_plus_par"))
    flow_steps = [
        (("Inputs" if en else "Datagrunnlag"), f'{plan["expected_covers"]} {"guests" if en else "gjester"}', covers_source, False),
        (("AI forecast" if en else "AI-prognose"), forecast_source, f'{len(forecast.get("dishes", []))} {"dish predictions" if en else "rettsprognoser"}', validation_fallback),
        (("Validation" if en else "Validering"), validation_value, str(forecast_note or "—"), validation_fallback),
        (("Deterministic math" if en else "Deterministisk beregning"), f'FEFO · {fefo_count} {"batch uses" if en else "batchuttak"}', planning_basis, False),
        (("Published plan" if en else "Publisert plan"), briefing_source, str(plan.get("generated_at", "—")), briefing_source == "deterministic_fallback"),
    ]
    flow_items = "".join(
        f'<li class="flow-step{" flow-step--fallback" if fallback else ""}"><div class="flow-top"><span class="flow-number">{number}</span>'
        f'<span class="flow-label">{escape(label)}</span></div><strong class="flow-value">{escape(value)}</strong>'
        f'<span class="flow-detail">{escape(detail)}</span></li>'
        for number, (label, value, detail, fallback) in enumerate(flow_steps, 1)
    )
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
    short_card_class = "card card--alert" if shortfalls else "card"
    return f"""<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kitchen Prep — {escape(plan['date'])}</title><style>{_STYLE}</style></head><body><main class="shell">
<nav class="topbar">{brand}{switch}</nav>
<header class="hero"><div class="hero-row"><div class="hero-copy"><p class="eyebrow">{"Daily operations plan" if en else "Dagens driftsplan"}</p>
<h1>{"A complete kitchen plan, before service" if en else "En komplett kjøkkenplan, før service"}</h1>
<span class="hero-kicker">{"Ready for service" if en else "Klar for service"}</span>
<p>{"From demand signals to safe prep and ordering decisions" if en else "Fra etterspørselssignaler til trygge prep- og bestillingsbeslutninger"}<br>{escape(plan['date'])} · {escape(str(plan.get('generated_at', '')))}</p>
<nav class="hero-actions" aria-label="Quick navigation">
<a class="hero-link" href="#agent-run">{"Agent run" if en else "Agentkjøring"} ↓</a>
<a class="hero-link" href="#prep-plan">{"Prep plan" if en else "Prep-plan"} ↓</a>
<a class="hero-link" href="#orders">{"Orders" if en else "Bestillinger"} ↓</a>
<a class="hero-link" href="#forecast">{"Forecast" if en else "Prognose"} ↓</a></nav></div>
<span class="{status_class}"><span class="dot"></span>{escape(status)}</span></div></header>

<section class="value-strip" aria-label="{"Why this matters" if en else "Hvorfor dette betyr noe"}">
<div class="value-card"><span class="value-icon">↻</span><div><strong>{"Autonomous" if en else "Autonom"}</strong><span>{"Runs before the team arrives" if en else "Kjører før teamet kommer"}</span></div></div>
<div class="value-card"><span class="value-icon">✓</span><div><strong>{"Safe quantities" if en else "Trygge mengder"}</strong><span>{"Python owns every operational number" if en else "Python eier alle operative tall"}</span></div></div>
<div class="value-card"><span class="value-icon">◎</span><div><strong>{"Auditable" if en else "Reviderbar"}</strong><span>{"Sources, fallbacks and history stay visible" if en else "Kilder, fallback og historikk er synlig"}</span></div></div>
</section>

<section class="cards" aria-label="Key metrics">
<div class="card"><span class="label">{"Expected guests" if en else "Forventede gjester"}</span><span class="value">{escape(str(plan['expected_covers']))}</span></div>
<div class="card"><span class="label">{"Prep tasks" if en else "Prep-oppgaver"}</span><span class="value">{len(prep)}</span></div>
<div class="{short_card_class}"><span class="label">{"Shortfalls" if en else "Mangler"}</span><span class="value">{len(shortfalls)}</span></div>
<div class="card"><span class="label">{"Orders" if en else "Bestillinger"}</span><span class="value">{len(orders)}</span></div>
</section>

<section class="panel run-flow" id="agent-run" aria-labelledby="run-flow-title"><header class="panel-head">
<h2 id="run-flow-title">{"Autonomous run" if en else "Autonom kjøring"}</h2>
<p>{"One traceable path from operational inputs to a published plan" if en else "Ett sporbart løp fra driftsdata til publisert plan"}</p>
</header><ol class="flow-list">{flow_items}</ol></section>

<div class="grid"><div class="stack">
{f'<section class="panel"><header class="panel-head"><h2>{"Plan history" if en else "Planhistorikk"}</h2><p>{"Read-only Firestore plans" if en else "Skrivebeskyttede Firestore-planer"}</p></header><div class="driver-list">{history_block}</div></section>' if history_block else ''}
<section class="panel"><header class="panel-head"><h2>{"Agent briefing" if en else "Agentbriefing"}</h2><p>{"AI recommendations; arithmetic remains deterministic" if en else "AI-anbefalinger; beregningene er fortsatt deterministiske"}</p></header>{briefing_content}</section>
<section class="panel" id="prep-plan"><header class="panel-head"><h2>{"Prioritized prep" if en else "Prioritert prep"}</h2><p>{"What the kitchen should start first" if en else "Det kjøkkenet bør starte med først"}</p></header>{prep_block}</section>
<section class="panel"><header class="panel-head"><h2>{"Today’s shortfalls" if en else "Mangler i dag"}</h2><p>{"Required for service, separate from replenishment" if en else "Behov til service, adskilt fra bestilling"}</p></header>{short_block}</section>
<section class="panel" id="orders"><header class="panel-head"><h2>{"Replenishment orders" if en else "Bestillinger til par"}</h2><p>{"Calculated from inventory remaining after today’s consumption" if en else "Beregnet fra lager etter dagens forbruk"}</p></header>{order_block}</section>
</div><aside class="stack">
<section class="panel"><header class="panel-head"><h2>{"Run integrity" if en else "Kjøringsintegritet"}</h2><p>{"Model paths and audit status" if en else "Modellbaner og revisjonsstatus"}</p></header>
<div class="source"><span>{"Forecast" if en else "Prognose"}</span><strong>{escape(str(forecast.get('forecast_source', '')))}</strong></div>
<div class="source"><span>{"Briefing" if en else "Briefing"}</span><strong>{escape(str(plan.get('briefing_source', '')))}</strong></div>
<div class="source"><span>{"Inventory" if en else "Lager"}</span><strong>{escape(str(plan.get('inventory_basis', 'seed_inventory')))}</strong></div>
<div class="source"><span>{"Diagnostic" if en else "Diagnostikk"}</span><strong>{escape(str(forecast_note or '—'))}</strong></div></section>
<section class="panel" id="forecast"><header class="panel-head"><h2>{"Forecast drivers" if en else "Prognosedrivere"}</h2><p>{"Signals used by the validated demand proposal" if en else "Signaler brukt i validert etterspørselsforslag"}</p></header><div class="driver-list">{driver_block or '<span class="chip">—</span>'}</div>{forecast_rows}</section>
<section class="panel"><header class="panel-head"><h2>{"Expired waste" if en else "Utgått svinn"}</h2><p>{"Removed before FEFO consumption" if en else "Fjernet før FEFO-forbruk"}</p></header>{waste_block}</section>
</aside></div>
<footer class="footer">{"Gemini judgment · deterministic arithmetic · Firestore audit trail" if en else "Gemini-vurdering · deterministiske beregninger · Firestore-spor"}</footer>
</main></body></html>"""
