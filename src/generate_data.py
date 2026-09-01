from pathlib import Path
import numpy as np
import pandas as pd

RNG_SEED = 42

def generate_marketplace_panel(n_properties=500, n_weeks=52, seed=RNG_SEED):
    rng = np.random.default_rng(seed)

    property_id = np.arange(n_properties)
    quality = rng.beta(4, 2, size=n_properties)
    baseline_visibility = rng.beta(2, 3, size=n_properties)
    base_demand = rng.lognormal(mean=2.6, sigma=0.45, size=n_properties)

    rows = []
    recent_shock = np.zeros(n_properties)
    adopted = np.zeros(n_properties, dtype=bool)
    adoption_week = np.full(n_properties, np.nan)

    for week in range(n_weeks):
        seasonality = 1.0 + 0.15 * np.sin(2 * np.pi * week / 26)
        market_shock = rng.normal(0, 0.05)

        latent_growth = 0.55 * recent_shock + rng.normal(0, 0.12, size=n_properties)
        recent_shock = latent_growth

        # Voluntary adoption: properties with stronger recent demand,
        # higher quality, and lower baseline visibility are more likely to adopt.
        eligible = ~adopted
        logit = (
            -5.4
            + 1.1 * quality
            - 0.9 * baseline_visibility
            + 1.4 * latent_growth
            + 0.035 * week
        )
        p_adopt = 1 / (1 + np.exp(-logit))
        new_adopt = eligible & (rng.random(n_properties) < p_adopt)
        adopted[new_adopt] = True
        adoption_week[new_adopt] = week

        treated = adopted.astype(int)
        event_time = np.where(adopted, week - adoption_week, np.nan)

        # True treatment effect: strongest for low-visibility suppliers,
        # ramps up over the first few weeks, then stabilizes.
        exposure_ramp = np.where(
            treated == 1,
            1 - np.exp(-np.maximum(event_time, 0) / 3.0),
            0.0,
        )
        true_booking_lift = treated * exposure_ramp * (0.08 + 0.22 * (1 - baseline_visibility))

        untreated_bookings = (
            base_demand
            * seasonality
            * np.exp(0.55 * quality + 0.35 * baseline_visibility + latent_growth + market_shock)
        )

        expected_bookings = untreated_bookings * (1 + true_booking_lift)
        bookings = rng.poisson(np.maximum(expected_bookings, 0.1))

        avg_price = 95 + 85 * quality + rng.normal(0, 5, size=n_properties)
        revenue = bookings * np.maximum(avg_price, 25)

        impressions = np.maximum(
            20,
            untreated_bookings * (18 + 16 * baseline_visibility) * (1 + 0.35 * treated)
            + rng.normal(0, 25, size=n_properties)
        ).astype(int)

        clicks = rng.binomial(impressions, np.clip(0.035 + 0.025 * quality + 0.015 * treated, 0.01, 0.20))

        for i in range(n_properties):
            rows.append({
                "property_id": int(property_id[i]),
                "week": int(week),
                "quality_score": float(quality[i]),
                "baseline_visibility": float(baseline_visibility[i]),
                "recent_demand_growth": float(latent_growth[i]),
                "treated": int(treated[i]),
                "adoption_week": None if np.isnan(adoption_week[i]) else int(adoption_week[i]),
                "event_time": None if np.isnan(event_time[i]) else int(event_time[i]),
                "impressions": int(impressions[i]),
                "clicks": int(clicks[i]),
                "bookings": int(bookings[i]),
                "revenue": float(revenue[i]),
                "true_booking_lift_pct": float(true_booking_lift[i] * 100),
            })

    df = pd.DataFrame(rows)

    # Backfill each eventual adopter's first treatment week across its full history.
    # This is essential for valid pre-treatment event-time diagnostics.
    first_treat = (
        df.loc[df["treated"] == 1]
        .groupby("property_id")["week"]
        .min()
    )
    df["adoption_week"] = df["property_id"].map(first_treat)
    df["event_time"] = df["week"] - df["adoption_week"]
    df.loc[df["adoption_week"].isna(), "event_time"] = np.nan

    return df


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "marketplace_panel.csv"
    out.parent.mkdir(exist_ok=True)
    df = generate_marketplace_panel()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}")
    print(f"Properties: {df.property_id.nunique():,}")
    print(f"Ever treated: {df.groupby('property_id').treated.max().mean():.1%}")
