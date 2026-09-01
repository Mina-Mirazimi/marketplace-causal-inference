from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marketplace_panel.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

def load_data():
    return pd.read_csv(DATA)

def naive_difference(df):
    means = df.groupby("treated")["bookings"].mean()
    return float(means.loc[1] - means.loc[0])

def twfe(df):
    # Log outcome makes the treatment coefficient approximately interpretable as a percentage change.
    d = df.copy()
    d["log_bookings"] = np.log1p(d["bookings"])
    model = smf.ols(
        "log_bookings ~ treated + C(property_id) + C(week)",
        data=d
    ).fit(cov_type="cluster", cov_kwds={"groups": d["property_id"]})
    return model

def event_study(df, min_event=-8, max_event=12, reference=-1):
    d = df.copy()
    d = d[d["event_time"].between(min_event, max_event) | d["event_time"].isna()].copy()
    d["log_bookings"] = np.log1p(d["bookings"])

    event_cols = []
    for k in range(min_event, max_event + 1):
        if k == reference:
            continue
        name = f"event_{'m' + str(abs(k)) if k < 0 else 'p' + str(k)}"
        d[name] = (d["event_time"] == k).astype(int)
        event_cols.append((k, name))

    rhs = " + ".join(name for _, name in event_cols)
    formula = f"log_bookings ~ {rhs} + C(property_id) + C(week)"
    model = smf.ols(formula, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["property_id"]}
    )

    rows = []
    for k, name in event_cols:
        rows.append({
            "event_time": k,
            "coef": model.params.get(name, np.nan),
            "se": model.bse.get(name, np.nan),
        })
    out = pd.DataFrame(rows)
    out["ci_low"] = out["coef"] - 1.96 * out["se"]
    out["ci_high"] = out["coef"] + 1.96 * out["se"]
    return model, out

def heterogeneous_effects(df):
    d = df.copy()
    d["visibility_group"] = pd.qcut(
        d["baseline_visibility"],
        q=3,
        labels=["Low visibility", "Medium visibility", "High visibility"],
    )
    d["log_bookings"] = np.log1p(d["bookings"])
    model = smf.ols(
        "log_bookings ~ treated * C(visibility_group) + C(property_id) + C(week)",
        data=d
    ).fit(cov_type="cluster", cov_kwds={"groups": d["property_id"]})
    return model

def main():
    df = load_data()

    naive = naive_difference(df)
    twfe_model = twfe(df)
    _, es = event_study(df)
    het_model = heterogeneous_effects(df)

    summary = pd.DataFrame({
        "metric": [
            "rows",
            "properties",
            "ever_treated_share",
            "naive_booking_difference",
            "twfe_log_effect",
            "twfe_approx_pct_effect",
        ],
        "value": [
            len(df),
            df["property_id"].nunique(),
            df.groupby("property_id")["treated"].max().mean(),
            naive,
            twfe_model.params["treated"],
            (np.exp(twfe_model.params["treated"]) - 1) * 100,
        ],
    })

    summary.to_csv(RESULTS / "model_summary.csv", index=False)
    es.to_csv(RESULTS / "event_study.csv", index=False)
    (RESULTS / "twfe_summary.txt").write_text(twfe_model.summary().as_text())
    (RESULTS / "heterogeneity_summary.txt").write_text(het_model.summary().as_text())

    print(summary.to_string(index=False))
    print(f"\nSaved results to {RESULTS}")

if __name__ == "__main__":
    main()
