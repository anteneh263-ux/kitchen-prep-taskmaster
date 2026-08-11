from datetime import date

from kitchen_prep import config
from kitchen_prep.data_access import menu as menu_da
from kitchen_prep.data_access import sales as sales_da


def test_sales_history_no_future_leakage():
    end = date.fromisoformat(config.SALES_HISTORY_END)
    demo = date.fromisoformat(config.DEMO_DATE)
    for r in sales_da.load_sales_rows():
        d = date.fromisoformat(r["date"])
        assert d <= end
        assert d < demo


def test_all_dishes_present_and_known():
    rows = sales_da.load_sales_rows()
    seen = {r["dish_id"] for r in rows}
    assert seen == set(menu_da.dish_ids())


def test_dishes_per_cover_ratio_in_band():
    rows = sales_da.load_sales_rows()
    by_date: dict[str, list] = {}
    for r in rows:
        by_date.setdefault(r["date"], []).append(r)
    for d, rs in by_date.items():
        ratio = sum(x["qty_sold"] for x in rs) / rs[0]["covers"]
        assert config.RATIO_MIN <= ratio <= config.RATIO_MAX, (d, ratio)


def test_baseline_has_enough_history_for_demo():
    # At least 4 same-weekday observations before the demo date for each dish.
    for dish_id in menu_da.dish_ids():
        hist = sales_da.same_weekday_history(config.DEMO_DATE, dish_id, weeks=4)
        assert len(hist) == 4
