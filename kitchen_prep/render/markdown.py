"""Render the authoritative plan + validated briefing JSON into Markdown."""
from __future__ import annotations


def render(plan: dict) -> str:
    b = plan["briefing"]
    lines: list[str] = []
    lines.append(f"# Kitchen briefing — {plan['date']}")
    lines.append("")
    lines.append(b["summary"])
    lines.append("")

    lines.append(f"**Expected guests:** {plan['expected_covers']}  ")
    lines.append(f"**Forecast source:** {plan['forecast']['forecast_source']}  ")
    lines.append(f"**Planning basis:** {plan['planning_basis']}")
    lines.append("")

    lines.append("## Prioritized prep")
    lines.append("")
    for t in sorted(plan["prep_tasks"], key=lambda t: t["priority"]):
        lines.append(f"{t['priority']}. {t['dish_id']} — {t['qty']} stk ({t['prep_minutes']} min)")
    lines.append("")

    if plan["prep_shortfalls"]:
        lines.append("## Today's shortfalls")
        lines.append("")
        for s in plan["prep_shortfalls"]:
            lines.append(
                f"- {s['item_id']}: requires {s['required']}, available {s['available']} "
                f"→ shortfall {s['shortfall']}"
            )
        lines.append("")

    if plan["replenishment_orders"]:
        lines.append("## Replenishment orders (to par)")
        lines.append("")
        for o in plan["replenishment_orders"]:
            lines.append(
                f"- {o['item_id']}: order {o['order_qty']} {o['unit']} from "
                f"{o['supplier']} (delivery {o['delivery_date']})"
            )
        lines.append("")

    if plan["waste_flagged"]:
        lines.append("## Discard (expired)")
        lines.append("")
        for w in plan["waste_flagged"]:
            lines.append(f"- {w['batch_id']} {w['item_id']} ({w['qty']}) expired {w['expiry_date']}")
        lines.append("")

    if b["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for w in b["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
