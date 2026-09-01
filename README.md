# Marketplace Causal Inference

**Estimating the Incremental Effect of Sponsored Advertising in a Two-Sided Marketplace**

This project demonstrates how an economist/data scientist can evaluate whether a marketplace advertising program *causes* higher bookings and revenue when participation is voluntary and treatment timing is endogenous.

## Business question

A marketplace offers suppliers (for example, hotels, hosts, or merchants) a sponsored-advertising program that can increase visibility. Management observes that advertisers have higher bookings, but that comparison is not causal: high-demand or fast-growing suppliers may be more likely to start advertising.

The core decision is:

> **Does sponsored advertising create incremental bookings and revenue, for whom, and when is the program economically worthwhile?**

## Why naive analysis can fail

Suppliers self-select into advertising. In the simulated data, adoption probability depends on recent demand, baseline quality, and marketplace visibility. This creates selection bias.

A simple comparison of treated and untreated suppliers can therefore overstate or understate the true incremental effect.

## Empirical strategy

The project compares several approaches:

1. **Naive cross-sectional comparison**
2. **Two-way fixed effects (TWFE)** with supplier and week fixed effects
3. **Event-study estimates** around treatment adoption
4. **Cohort-aware dynamic effects** using treatment timing
5. **Heterogeneous treatment effects** by baseline visibility
6. **Robustness checks** for pre-trends and alternative outcome definitions

The simulated data include a known data-generating process, so estimated effects can be compared with the true causal effect.

## Dataset

Synthetic weekly panel data contain:

- supplier/property ID
- week
- treatment status
- treatment adoption week
- impressions
- clicks
- bookings
- revenue
- baseline visibility
- quality score
- market demand index
- recent demand growth
- true treatment effect

The default generator creates thousands of suppliers observed for one year.

## Repository structure

```text
marketplace-causal-inference/
│
├── README.md
├── requirements.txt
├── src/
│   ├── generate_data.py
│   ├── analysis.py
│   └── plotting.py
├── sql/
│   └── marketplace_metrics.sql
├── notebooks/
│   └── marketplace_causal_analysis.ipynb
├── tests/
│   └── test_data_generation.py
├── data/
└── results/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/generate_data.py
python src/analysis.py
```

The scripts write the synthetic panel to `data/marketplace_panel.csv` and model outputs to `results/`.

## Key modeling idea

For supplier \(i\) in week \(t\):

\[
Y_{it} = \alpha_i + \gamma_t + \tau_{it}D_{it} + \epsilon_{it}
\]

where \(D_{it}\) is advertising participation. Treatment adoption is intentionally endogenous in the simulation, so identification requires exploiting within-supplier changes over time and checking pre-treatment dynamics.

## Business interpretation

The analysis is designed to answer more than whether an estimate is statistically significant. It asks:

- Is the effect economically meaningful?
- Does it persist after adoption?
- Is it concentrated among low-visibility suppliers?
- Are pre-trends consistent with the identifying assumptions?
- Would broad enrollment or targeted enrollment create more value?

The intended output is a recommendation such as:

> Sponsored advertising generates positive incremental bookings on average, but gains are concentrated among suppliers with low baseline visibility. A targeted program can therefore create more incremental value than broad enrollment.

## Skills demonstrated

**Causal inference:** panel data, fixed effects, event studies, staggered adoption, pre-trend diagnostics, heterogeneous treatment effects  
**Data science:** Python, pandas, NumPy, statsmodels, reproducible analysis  
**Analytics engineering:** SQL metrics, modular code, tests, versionable outputs  
**Business translation:** incrementality, targeting, marketplace economics, decision-oriented reporting

## Important note

This is a portfolio project using fully synthetic data. It does not use proprietary or confidential data from any company.
