from src.generate_data import generate_marketplace_panel

def test_panel_shape_and_columns():
    df = generate_marketplace_panel(n_properties=50, n_weeks=10, seed=1)
    assert len(df) == 500
    required = {
        "property_id", "week", "treated", "adoption_week", "event_time",
        "bookings", "revenue", "baseline_visibility", "true_booking_lift_pct"
    }
    assert required.issubset(df.columns)

def test_treatment_is_absorbing():
    df = generate_marketplace_panel(n_properties=100, n_weeks=20, seed=2)
    for _, g in df.groupby("property_id"):
        vals = g.sort_values("week")["treated"].tolist()
        assert vals == sorted(vals)
