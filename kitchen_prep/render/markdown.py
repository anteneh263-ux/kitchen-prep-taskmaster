"""Render the authoritative plan + validated briefing JSON into Markdown."""
from __future__ import annotations


def render(plan: dict) -> str:
    b = plan["briefing"]
    lines: list[str] = []
    lines.append(f"# Kjøkken-brief — {plan['date']}")
    lines.append("")
    lines.append(b["summary"])
    lines.append("")

    lines.append(f"**Forventede gjester:** {plan['expected_covers']}  ")
    lines.append(f"**Prognosekilde:** {plan['forecast']['forecast_source']}  ")
    lines.append(f"**Planleggingsgrunnlag:** {plan['planning_basis']}")
    lines.append("")

    lines.append("## Prep (prioritert)")
    lines.append("")
    for t in sorted(plan["prep_tasks"], key=lambda t: t["priority"]):
        lines.append(f"{t['priority']}. {t['dish_id']} — {t['qty']} stk ({t['prep_minutes']} min)")
    lines.append("")

    if plan["prep_shortfalls"]:
        lines.append("## Mangel i dag")
        lines.append("")
        for s in plan["prep_shortfalls"]:
            lines.append(
                f"- {s['item_id']}: trenger {s['required']}, har {s['available']} "
                f"→ mangel {s['shortfall']}"
            )
        lines.append("")

    if plan["replenishment_orders"]:
        lines.append("## Bestillinger (opp til par)")
        lines.append("")
        for o in plan["replenishment_orders"]:
            lines.append(
                f"- {o['item_id']}: bestill {o['order_qty']} {o['unit']} fra "
                f"{o['supplier']} (levering {o['delivery_date']})"
            )
        lines.append("")

    if plan["waste_flagged"]:
        lines.append("## Kast (utløpt)")
        lines.append("")
        for w in plan["waste_flagged"]:
            lines.append(f"- {w['batch_id']} {w['item_id']} ({w['qty']}) utløpt {w['expiry_date']}")
        lines.append("")

    if b["warnings"]:
        lines.append("## Advarsler")
        lines.append("")
        for w in b["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
