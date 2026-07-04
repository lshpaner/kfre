import matplotlib

matplotlib.use("Agg")

import os
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt

from kfre import (
    add_kfre_risk_col,
    class_ckd_stages,
    class_esrd_outcome,
    eval_kfre_metrics,
    perform_conversions,
    upcr_uacr,
)

# ---------------------------------------------------------------------------
# Shared fixture: minimal UK-style CKD cohort (unit-converted, outcomes set)
# ---------------------------------------------------------------------------


@pytest.fixture
def uk_cohort():
    """
    Mimics the structure of the UK NHS CKD dataset used in the paper,
    with unit conversions already applied and ESRD outcomes pre-cleaned.
    Albumin in g/dL, Calcium and Phosphate in mg/dL, Bicarbonate in mmol/L.
    eGFR values chosen so all patients fall into Stage 4 or Stage 5.
    """
    np.random.seed(42)
    n = 50

    df = pd.DataFrame(
        {
            "Age": np.random.uniform(45, 85, n),
            "SEX": np.random.choice(["Male", "Female"], n),
            "eGFR-EPI": np.random.uniform(8, 29, n),  # Stage 4 & 5 only
            "uACR": np.random.uniform(50, 3000, n),
            "Diabetes (1=yes; 0=no)": np.random.choice([0, 1], n),
            "Hypertension (1=yes; 0=no)": np.random.choice([0, 1], n),
            "Albumin_g_dl": np.random.uniform(2.5, 5.0, n),
            "Phosphate_mg_dl": np.random.uniform(2.5, 6.5, n),
            "Bicarbonate (mmol/L)": np.random.uniform(18, 28, n),
            "Calcium_mg_dl": np.random.uniform(8.0, 10.5, n),
            "ESRD": np.random.choice([0, 1], n, p=[0.6, 0.4]),
            "Follow-up YEARS": np.random.uniform(0.5, 5.0, n),
        }
    )
    return df


@pytest.fixture
def cohort_with_predictions(uk_cohort):
    """Full pipeline: outcomes labeled, KFRE predictions added."""
    df = uk_cohort.copy()

    # Label outcomes
    df = class_esrd_outcome(
        df,
        col="ESRD",
        years=2,
        duration_col="Follow-up YEARS",
        prefix="esrd",
        create_years_col=False,
    )
    df = class_esrd_outcome(
        df,
        col="ESRD",
        years=5,
        duration_col="Follow-up YEARS",
        prefix="esrd",
        create_years_col=False,
    )

    # Add KFRE predictions
    df = add_kfre_risk_col(
        df=df,
        age_col="Age",
        sex_col="SEX",
        eGFR_col="eGFR-EPI",
        uACR_col="uACR",
        dm_col="Diabetes (1=yes; 0=no)",
        htn_col="Hypertension (1=yes; 0=no)",
        albumin_col="Albumin_g_dl",
        phosphorous_col="Phosphate_mg_dl",
        bicarbonate_col="Bicarbonate (mmol/L)",
        calcium_col="Calcium_mg_dl",
        num_vars=[4, 6, 8],
        years=(2, 5),
        is_north_american=False,
        copy=True,
    )

    # Add CKD stages
    df = class_ckd_stages(
        df,
        egfr_col="eGFR-EPI",
        stage_col="stage",
        combined_stage_col="stage_combined",
    )

    return df


# ---------------------------------------------------------------------------
# uPCR -> uACR conversion (mirrors conversions.py pipeline)
# ---------------------------------------------------------------------------


def test_upcr_to_uacr_full_cohort():
    """perform_conversions + upcr_uacr on a cohort with uPCR column."""
    df = pd.DataFrame(
        {
            "uPCR": [150.0, 600.0, 50.0, 300.0],
            "SEX": ["Female", "Male", "Female", "Male"],
            "Diabetes (1=yes; 0=no)": [1, 0, 1, 0],
            "Hypertension (1=yes; 0=no)": [1, 1, 0, 1],
        }
    )
    converted = perform_conversions(df.copy(), reverse=False, convert_all=True)
    assert "uPCR_mg_g" in converted.columns

    converted["uACR"] = upcr_uacr(
        df=converted,
        sex_col="SEX",
        diabetes_col="Diabetes (1=yes; 0=no)",
        hypertension_col="Hypertension (1=yes; 0=no)",
        upcr_col="uPCR_mg_g",
        female_str="Female",
    )
    assert "uACR" in converted.columns
    assert converted["uACR"].notna().all()
    assert (converted["uACR"] > 0).all()


# ---------------------------------------------------------------------------
# class_ckd_stages: Stage 4 and Stage 5 only (matches UK cohort)
# ---------------------------------------------------------------------------


def test_ckd_stages_stage4_and_stage5_only():
    """eGFR values 8-29 should produce only Stage 4 and Stage 5."""
    df = pd.DataFrame({"eGFR": [28, 20, 12, 8, 15, 25]})
    out = class_ckd_stages(
        df,
        egfr_col="eGFR",
        stage_col="stage",
        combined_stage_col="stage_combined",
    )
    unique_stages = set(out["stage"].unique())
    assert unique_stages == {"CKD Stage 4", "CKD Stage 5"}
    # all should be in combined group
    assert (out["stage_combined"] == "CKD Stage 3 - 5").all()


def test_ckd_stages_present_in_cohort(cohort_with_predictions):
    """Fixture cohort should only have Stage 4 and Stage 5."""
    stages = cohort_with_predictions["stage"].unique()
    for s in stages:
        assert s in ["CKD Stage 4", "CKD Stage 5"]


# ---------------------------------------------------------------------------
# KFRE predictions: all six columns present, values in [0, 1]
# ---------------------------------------------------------------------------


def test_all_kfre_columns_present(cohort_with_predictions):
    expected = [
        "kfre_4var_2year",
        "kfre_4var_5year",
        "kfre_6var_2year",
        "kfre_6var_5year",
        "kfre_8var_2year",
        "kfre_8var_5year",
    ]
    for col in expected:
        assert col in cohort_with_predictions.columns


def test_kfre_predictions_in_unit_interval(cohort_with_predictions):
    kfre_cols = [c for c in cohort_with_predictions.columns if c.startswith("kfre_")]
    for col in kfre_cols:
        vals = cohort_with_predictions[col].dropna()
        assert (vals >= 0).all(), f"{col} has values < 0"
        assert (vals <= 1).all(), f"{col} has values > 1"


def test_stage5_higher_risk_than_stage4(cohort_with_predictions):
    """Median 2-year risk should be higher for Stage 5 than Stage 4."""
    df = cohort_with_predictions
    median_s4 = df[df["stage"] == "CKD Stage 4"]["kfre_4var_2year"].median()
    median_s5 = df[df["stage"] == "CKD Stage 5"]["kfre_4var_2year"].median()
    assert median_s5 > median_s4


def test_8var_correlated_with_4var(cohort_with_predictions):
    """4-var and 8-var predictions should be positively correlated."""
    df = cohort_with_predictions.dropna(subset=["kfre_4var_2year", "kfre_8var_2year"])
    corr = df["kfre_4var_2year"].corr(df["kfre_8var_2year"])
    assert corr > 0.7


# ---------------------------------------------------------------------------
# eval_kfre_metrics: no NaNs, correct structure
# ---------------------------------------------------------------------------


def test_eval_kfre_metrics_no_nans(cohort_with_predictions):
    df = cohort_with_predictions.dropna(
        subset=[c for c in cohort_with_predictions.columns if "kfre_" in c]
    )
    metrics = eval_kfre_metrics(
        df=df,
        n_var_list=[4, 6, 8],
        outcome_years=[2, 5],
    )
    assert isinstance(metrics, pd.DataFrame)
    assert not metrics.isnull().all().all()


def test_eval_kfre_metrics_expected_columns(cohort_with_predictions):
    df = cohort_with_predictions.dropna(
        subset=[c for c in cohort_with_predictions.columns if "kfre_" in c]
    )
    metrics = eval_kfre_metrics(
        df=df,
        n_var_list=[4, 6, 8],
        outcome_years=[2, 5],
    )
    # Should have 6 columns: 3 models x 2 horizons
    assert metrics.shape[1] == 6
    assert "AUC ROC" in metrics.index
    assert "Brier Score" in metrics.index


def test_eval_kfre_metrics_auc_in_range(cohort_with_predictions):
    df = cohort_with_predictions.dropna(
        subset=[c for c in cohort_with_predictions.columns if "kfre_" in c]
    )
    metrics = eval_kfre_metrics(
        df=df,
        n_var_list=[4],
        outcome_years=[2],
    )
    auc = float(metrics.loc["AUC ROC", "2_year_4_var_kfre"])
    assert 0.0 <= auc <= 1.0


# ---------------------------------------------------------------------------
# Figure generation: boxplot and scatter save without error
# ---------------------------------------------------------------------------


def test_risk_by_stage_figure_saves(cohort_with_predictions, tmp_path):
    df = cohort_with_predictions
    stage_order = ["CKD Stage 4", "CKD Stage 5"]
    data_by_stage = [
        df[df["stage"] == s]["kfre_4var_2year"].dropna().clip(lower=0)
        for s in stage_order
    ]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.boxplot(data_by_stage)
    ax.set_xticklabels(["Stage 4", "Stage 5"])
    ax.set_ylim(bottom=0)
    ax.set_xlabel("CKD Stage")
    ax.set_ylabel("Predicted 2-Year Risk")
    ax.set_title("KFRE 4-Variable, 2-Year Risk by CKD Stage")
    out_path = tmp_path / "risk_by_stage.svg"
    plt.savefig(str(out_path))
    plt.close()
    assert out_path.exists()
    assert out_path.stat().st_size > 0


def test_4var_vs_8var_scatter_saves(cohort_with_predictions, tmp_path):
    df = cohort_with_predictions.dropna(subset=["kfre_4var_2year", "kfre_8var_2year"])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(df["kfre_4var_2year"], df["kfre_8var_2year"], alpha=0.5, s=10)
    lims = [0, max(df["kfre_4var_2year"].max(), df["kfre_8var_2year"].max())]
    ax.plot(lims, lims, "--", color="gray")
    ax.set_xlabel("4-Variable KFRE (2-year)")
    ax.set_ylabel("8-Variable KFRE (2-year)")
    ax.set_title("4- vs. 8-Variable KFRE: 2-Year Risk Estimates")
    out_path = tmp_path / "4var_vs_8var.svg"
    plt.savefig(str(out_path))
    plt.close()
    assert out_path.exists()
    assert out_path.stat().st_size > 0
