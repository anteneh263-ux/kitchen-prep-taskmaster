"""Server-rendered, mobile-friendly HTML view of the latest plan.

Pure function (no web framework) so it is trivially unit-testable. The FastAPI
route in ``server.py`` wraps the output in an HTMLResponse.
"""
from __future__ import annotations

from html import escape


def _run_status(plan: dict, language: str) -> str:
    sources = {plan["forecast"]["forecast_source"], plan.get("briefing_source", "")}
    if "deterministic_fallback" in sources:
        return "DEGRADED (fallback used)" if language == "en" else "DEGRADERT (fallback brukt)"
    return "OK"


_STYLE = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif;
  margin: 0; padding: 1rem; max-width: 640px; margin-inline: auto; line-height: 1.45; }
h1 { font-size: 1.25rem; margin: 0 0 .25rem; }
h2 { font-size: 1rem; margin: 1.25rem 0 .5rem; border-bottom: 1px solid #8883; padding-bottom: .2rem; }
.meta { color: #666; font-size: .85rem; }
.status-ok { color: #137333; font-weight: 600; }
.status-degraded { color: #b06000; font-weight: 600; }
ul { padding-left: 1.1rem; margin: .3rem 0; }
li { margin: .15rem 0; }
table { width: 100%; border-collapse: collapse; font-size: .9rem; }
th, td { text-align: left; padding: .3rem .4rem; border-bottom: 1px solid #8882; }
.empty { color: #888; font-style: italic; }
.pill { display: inline-block; background: #8882; border-radius: 999px; padding: .05rem .5rem; font-size: .8rem; }
.language { float: right; font-size: .85rem; }
""".strip()


def _empty(msg: str) -> str:
    return f'<p class="empty">{escape(msg)}</p>'


def render_home(plan: dict | None, language: str = "no") -> str:
    language = "en" if language == "en" else "no"
    en = language == "en"
    switch = (
        '<a class="language" href="?lang=no" lang="no">Norsk</a>'
        if en
        else '<a class="language" href="?lang=en" lang="en">English</a>'
    )
    if plan is None:
        empty_message = "No plan has been published yet." if en else "Ingen plan er publisert ennå."
        return (
            f"<!doctype html><html lang=\"{language}\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>Kitchen Prep</title><style>{_STYLE}</style></head><body>"
            f"{switch}"
            "<h1>Kitchen Prep Taskmaster</h1>"
            f"<p class=\"empty\">{empty_message}</p>"
            "</body></html>"
        )

    status = _run_status(plan, language)
    status_cls = "status-ok" if status == "OK" else "status-degraded"

    prep = sorted(plan["prep_tasks"], key=lambda t: t["priority"])
    prep_html = "".join(
        f"<li><span class=\"pill\">{t['priority']}</span> "
        f"{escape(t['dish_id'])} — {escape(str(t['qty']))} {'pcs' if en else 'stk'} "
        f"({escape(str(t['prep_minutes']))} min)</li>"
        for t in prep
    ) or ""
    prep_block = f"<ul>{prep_html}</ul>" if prep else _empty(
        "No prep tasks." if en else "Ingen prep-oppgaver."
    )

    short = plan["prep_shortfalls"]
    short_html = "".join(
        f"<li>{escape(s['item_id'])}: {'requires' if en else 'trenger'} {escape(str(s['required']))}, "
        f"{'available' if en else 'har'} {escape(str(s['available']))} → {'shortfall' if en else 'mangel'} "
        f"<strong>{escape(str(s['shortfall']))}</strong></li>"
        for s in short
    )
    short_block = f"<ul>{short_html}</ul>" if short else _empty(
        "No shortfalls today." if en else "Ingen mangler i dag."
    )

    orders = plan["replenishment_orders"]
    if orders:
        rows = "".join(
            f"<tr><td>{escape(o['item_id'])}</td>"
            f"<td>{escape(str(o['order_qty']))} {escape(o['unit'])}</td>"
            f"<td>{escape(o['supplier'])}</td>"
            f"<td>{escape(o['delivery_date'])}</td></tr>"
            for o in orders
        )
        orders_block = (
            f"<table><thead><tr><th>{'Item' if en else 'Vare'}</th>"
            f"<th>{'Order' if en else 'Bestill'}</th>"
            f"<th>{'Supplier' if en else 'Leverandør'}</th>"
            f"<th>{'Delivery' if en else 'Levering'}</th></tr></thead><tbody>{rows}</tbody></table>"
        )
    else:
        orders_block = _empty("No orders." if en else "Ingen bestillinger.")

    waste = plan["waste_flagged"]
    waste_html = "".join(
        f"<li>{escape(w['batch_id'])} {escape(w['item_id'])} "
        f"({escape(str(w['qty']))}) {'expired' if en else 'utløpt'} {escape(w['expiry_date'])}</li>"
        for w in waste
    )
    waste_block = f"<ul>{waste_html}</ul>" if waste else _empty(
        "No expired waste." if en else "Ingen svinn."
    )

    return f"""<!doctype html>
<html lang="{language}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kitchen Prep — {escape(plan['date'])}</title>
<style>{_STYLE}</style>
</head>
<body>
{switch}
<h1>{'Kitchen briefing' if en else 'Kjøkken-brief'} — {escape(plan['date'])}</h1>
<p><strong>{escape(str(plan['expected_covers']))}</strong> {'expected guests' if en else 'forventede gjester'}</p>
<p class="meta">
{'Forecast source' if en else 'Prognosekilde'}: {escape(plan['forecast']['forecast_source'])} ·
{'Briefing source' if en else 'Briefingkilde'}: {escape(str(plan.get('briefing_source', '')))}<br>
{'Generated' if en else 'Kjørt'}: {escape(str(plan.get('generated_at', '')))} ·
{'Status'}: <span class="{status_cls}">{escape(status)}</span>
</p>

<h2>{'Prep (prioritized)' if en else 'Prep (prioritert)'}</h2>
{prep_block}

<h2>{'Today’s shortfalls' if en else 'Mangler i dag'}</h2>
{short_block}

<h2>{'Replenishment orders' if en else 'Bestillinger (replenishment)'}</h2>
{orders_block}

<h2>{'Waste (expired batches)' if en else 'Svinn (utgåtte batcher)'}</h2>
{waste_block}
</body>
</html>
"""
