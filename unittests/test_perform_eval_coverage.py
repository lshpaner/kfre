"""
Tests targeting uncovered branches in perform_eval.py (class_esrd_outcome,
class_ckd_stages, plot_kfre_metrics, eval_kfre_metrics).
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt

from kfre import (
    class_esrd_outcome,
    class_ckd_stages,
    eval_kfre_metrics,
)
from kfre.perform_eval import plot_kfre_metrics


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _minimal_metrics_df(n_var_list, outcome_years):
    """Build a minimal DataFrame with KFRE prediction + outcome columns."""
    rows = 20
    np.random.seed(0)
    data = {}
    for n in n_var_list:
        for y in outcome_years:
            data[f"kfre_{n}var_{y}year"] = np.random.uniform(0, 1, rows)
    for y in outcome_years:
        data[f"{y}_year_outcome"] = np.random.randint(0, 2, rows)
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# class_esrd_outcome
# ---------------------------------------------------------------------------

class TestClassEsrdOutcome:

    def test_create_years_col_true_divides_by_365(self):
        """create_years_col=True: duration_col is in days, gets divided."""
        df = pd.DataFrame({"flag": [1, 0], "days": [365, 1000]})
        out = class_esrd_outcome(
            df.copy(), col="flag", years=1,
            duration_col="days", prefix=None, create_years_col=True,
        )
        assert "ESRD_duration_years" in out.columns
        assert abs(out["ESRD_duration_years"].iloc[0] - 365 / 365.25) < 0.01

    def test_create_years_col_false_uses_col_directly(self):
        """create_years_col=False: duration_col values used as-is (years)."""
        df = pd.DataFrame({"flag": [1, 1], "yrs": [0.5, 3.0]})
        out = class_esrd_outcome(
            df.copy(), col="flag", years=2,
            duration_col="yrs", prefix=None, create_years_col=False,
        )
        assert "ESRD_duration_years" not in out.columns
        # first row: flag=1, yrs=0.5 <= 2 -> 1
        assert out["2_year_outcome"].iloc[0] == 1
        # second row: flag=1, yrs=3.0 > 2 -> 0
        assert out["2_year_outcome"].iloc[1] == 0

    def test_prefix_none_produces_bare_column(self):
        df = pd.DataFrame({"e": [1], "d": [1.0]})
        out = class_esrd_outcome(
            df.copy(), col="e", years=5,
            duration_col="d", prefix=None, create_years_col=False,
        )
        assert "5_year_outcome" in out.columns

    def test_prefix_string_prepends_to_column(self):
        df = pd.DataFrame({"e": [1], "d": [1.0]})
        out = class_esrd_outcome(
            df.copy(), col="e", years=2,
            duration_col="d", prefix="esrd", create_years_col=False,
        )
        assert "esrd_2_year_outcome" in out.columns

    def test_existing_column_dropped_and_recreated(self):
        """If column already exists it gets dropped and recreated cleanly."""
        df = pd.DataFrame({
            "e": [1, 0],
            "d": [1.0, 3.0],
            "2_year_outcome": [99, 99],   # stale values
        })
        out = class_esrd_outcome(
            df.copy(), col="e", years=2,
            duration_col="d", prefix=None, create_years_col=False,
        )
        # should not contain stale 99 values
        assert 99 not in out["2_year_outcome"].values

    def test_flag_zero_never_produces_outcome_one(self):
        df = pd.DataFrame({"e": [0, 0], "d": [0.5, 0.5]})
        out = class_esrd_outcome(
            df.copy(), col="e", years=2,
            duration_col="d", prefix=None, create_years_col=False,
        )
        assert (out["2_year_outcome"] == 0).all()

    def test_five_year_horizon(self):
        df = pd.DataFrame({"e": [1, 1, 0], "d": [4.9, 5.1, 2.0]})
        out = class_esrd_outcome(
            df.copy(), col="e", years=5,
            duration_col="d", prefix=None, create_years_col=False,
        )
        assert out["5_year_outcome"].tolist() == [1, 0, 0]


# ---------------------------------------------------------------------------
# class_ckd_stages
# ---------------------------------------------------------------------------

class TestClassCkdStages:

    def test_all_six_stages_classified(self):
        df = pd.DataFrame({"eG": [95, 75, 52, 35, 20, 10]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col="stage", combined_stage_col="combined",
        )
        assert out["stage"].tolist() == [
            "CKD Stage 1", "CKD Stage 2", "CKD Stage 3a",
            "CKD Stage 3b", "CKD Stage 4", "CKD Stage 5",
        ]

    def test_combined_col_none_skips_combined(self):
        df = pd.DataFrame({"eG": [20]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col="stage", combined_stage_col=None,
        )
        assert "combined" not in out.columns

    def test_stage_col_none_skips_stage(self):
        df = pd.DataFrame({"eG": [20]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col=None, combined_stage_col="combined",
        )
        assert "stage" not in out.columns
        assert "combined" in out.columns

    def test_egfr_boundary_values(self):
        """Exact boundary eGFR values hit the right stage."""
        df = pd.DataFrame({"eG": [90, 60, 45, 30, 15]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col="stage", combined_stage_col=None,
        )
        assert out["stage"].tolist() == [
            "CKD Stage 1", "CKD Stage 2", "CKD Stage 3a",
            "CKD Stage 3b", "CKD Stage 4",
        ]

    def test_combined_not_classified_above_60(self):
        df = pd.DataFrame({"eG": [61, 90]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col=None, combined_stage_col="combined",
        )
        assert (out["combined"] == "Not Classified").all()

    def test_combined_classified_below_60(self):
        df = pd.DataFrame({"eG": [59, 30, 10]})
        out = class_ckd_stages(
            df.copy(), egfr_col="eG",
            stage_col=None, combined_stage_col="combined",
        )
        assert (out["combined"] == "CKD Stage 3 - 5").all()


# ---------------------------------------------------------------------------
# eval_kfre_metrics
# ---------------------------------------------------------------------------

class TestEvalKfreMetrics:

    def test_invalid_n_var_raises(self):
        df = _minimal_metrics_df([4], [2])
        with pytest.raises(ValueError, match="Invalid variable number"):
            eval_kfre_metrics(df, n_var_list=[3], outcome_years=[2])

    def test_invalid_outcome_year_raises(self):
        df = _minimal_metrics_df([4], [2])
        with pytest.raises(ValueError, match="Invalid value for year"):
            eval_kfre_metrics(df, n_var_list=[4], outcome_years=[3])

    def test_missing_outcome_col_raises(self):
        df = _minimal_metrics_df([4], [2])
        df = df.drop(columns=["2_year_outcome"])
        with pytest.raises(ValueError, match="2_year_outcome must exist"):
            eval_kfre_metrics(df, n_var_list=[4], outcome_years=[2])

    def test_outcome_years_as_int(self):
        """outcome_years as int (not list) should be coerced to list."""
        df = _minimal_metrics_df([4], [2])
        metrics = eval_kfre_metrics(df, n_var_list=[4], outcome_years=2)
        assert isinstance(metrics, pd.DataFrame)

    def test_outcome_years_as_tuple(self):
        """outcome_years as tuple should be coerced to list."""
        df = _minimal_metrics_df([4], [2])
        metrics = eval_kfre_metrics(df, n_var_list=[4], outcome_years=(2,))
        assert isinstance(metrics, pd.DataFrame)

    def test_all_metrics_present(self):
        df = _minimal_metrics_df([4, 6, 8], [2, 5])
        metrics = eval_kfre_metrics(df, n_var_list=[4, 6, 8], outcome_years=[2, 5])
        for m in ["Precision/PPV", "Average Precision", "Sensitivity",
                  "Specificity", "AUC ROC", "Brier Score"]:
            assert m in metrics.index

    def test_missing_kfre_col_produces_none_pred(self):
        """When a kfre column is missing the entry is skipped (pred=None)."""
        df = _minimal_metrics_df([4], [2])
        # add 5_year_outcome but NOT kfre_4var_5year
        df["5_year_outcome"] = np.random.randint(0, 2, len(df))
        metrics = eval_kfre_metrics(df, n_var_list=[4], outcome_years=[2, 5])
        # only the 2-year column should be present
        assert "2_year_4_var_kfre" in metrics.columns
        assert "5_year_4_var_kfre" not in metrics.columns

    def test_six_columns_for_3_models_2_years(self):
        df = _minimal_metrics_df([4, 6, 8], [2, 5])
        metrics = eval_kfre_metrics(df, n_var_list=[4, 6, 8], outcome_years=[2, 5])
        assert metrics.shape[1] == 6

    def test_decimal_places_respected(self):
        df = _minimal_metrics_df([4], [2])
        metrics = eval_kfre_metrics(
            df, n_var_list=[4], outcome_years=[2], decimal_places=2
        )
        auc = float(metrics.loc["AUC ROC"].iloc[0])
        # with 2 decimal places the value should not have more than 2 dp
        assert round(auc, 2) == auc

    def test_brier_score_in_range(self):
        df = _minimal_metrics_df([4], [2])
        metrics = eval_kfre_metrics(df, n_var_list=[4], outcome_years=[2])
        brier = float(metrics.loc["Brier Score"].iloc[0])
        assert 0.0 <= brier <= 1.0


# ---------------------------------------------------------------------------
# plot_kfre_metrics -- argument validation branches
# ---------------------------------------------------------------------------

class TestPlotKfreMetricsValidation:

    def _df(self):
        return _minimal_metrics_df([4], [2])

    def test_invalid_show_years_raises(self):
        df = self._df()
        with pytest.raises(ValueError, match="show_years"):
            plot_kfre_metrics(df, num_vars=4, show_years=[3])

    def test_invalid_plot_type_raises(self):
        df = self._df()
        with pytest.raises(ValueError, match="plot_type"):
            plot_kfre_metrics(df, num_vars=4, show_years=2, plot_type="bad_type")

    def test_save_plots_without_path_raises(self):
        df = self._df()
        with pytest.raises(ValueError, match="image_path"):
            plot_kfre_metrics(
                df, num_vars=4, show_years=2,
                save_plots=True,
                image_path_png=None, image_path_svg=None,
            )

    def test_missing_kfre_col_raises(self):
        df = pd.DataFrame({"2_year_outcome": [0, 1]})
        with pytest.raises(ValueError, match="Missing columns"):
            plot_kfre_metrics(df, num_vars=4, show_years=2)

    def test_missing_outcome_col_raises(self):
        df = _minimal_metrics_df([4], [2])
        df = df.drop(columns=["2_year_outcome"])
        with pytest.raises(ValueError, match="No outcome columns"):
            plot_kfre_metrics(df, num_vars=4, show_years=2)

    def test_show_years_as_int_coerced(self, monkeypatch):
        df = self._df()
        monkeypatch.setattr(plt, "show", lambda: None)
        # Should not raise -- int coerced to list
        result = plot_kfre_metrics(
            df, num_vars=4, mode="prep", show_years=2, plot_type="auc_roc"
        )
        assert result is not None

    def test_show_years_as_tuple_coerced(self, monkeypatch):
        df = self._df()
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4], mode="prep", show_years=(2,), plot_type="auc_roc"
        )
        assert result is not None

    def test_num_vars_as_tuple_coerced(self, monkeypatch):
        df = self._df()
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=(4,), mode="prep", show_years=2, plot_type="auc_roc"
        )
        assert result is not None

    def test_prep_mode_returns_tuple(self):
        df = self._df()
        result = plot_kfre_metrics(
            df, num_vars=4, mode="prep", show_years=2, plot_type="auc_roc"
        )
        y_true, preds, outcomes = result
        assert len(y_true) == 1
        assert "4var" in preds
        assert outcomes == ["2-year"]

    def test_mode_plot_returns_none(self, monkeypatch):
        df = self._df()
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=4, mode="plot", show_years=2, plot_type="auc_roc"
        )
        assert result is None

    def test_mode_both_returns_tuple(self, monkeypatch):
        df = self._df()
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=4, mode="both", show_years=2, plot_type="auc_roc"
        )
        assert result is not None

    def test_plot_combinations_auc_roc(self, monkeypatch):
        df = _minimal_metrics_df([4, 6], [2])
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=2, plot_type="auc_roc",
            plot_combinations=True,
        )
        assert result is not None

    def test_plot_combinations_pr_curve(self, monkeypatch):
        df = _minimal_metrics_df([4, 6], [2])
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=2, plot_type="precision_recall",
            plot_combinations=True,
        )
        assert result is not None

    def test_plot_combinations_all_plots(self, monkeypatch):
        df = _minimal_metrics_df([4, 6], [2])
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=2, plot_type="all_plots",
            plot_combinations=True,
        )
        assert result is not None

    def test_per_var_auc_roc(self, monkeypatch):
        df = _minimal_metrics_df([4, 6], [2])
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=2, plot_type="auc_roc",
            plot_combinations=False,
        )
        assert result is not None

    def test_per_var_pr_curve(self, monkeypatch):
        df = _minimal_metrics_df([4, 6], [2])
        monkeypatch.setattr(plt, "show", lambda: None)
        result = plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=2, plot_type="precision_recall",
            plot_combinations=False,
        )
        assert result is not None

    def test_show_subplots_saves(self, monkeypatch, tmp_path):
        df = _minimal_metrics_df([4, 6], [2, 5])
        monkeypatch.setattr(plt, "show", lambda: None)
        png_dir = tmp_path / "png"
        svg_dir = tmp_path / "svg"
        plot_kfre_metrics(
            df, num_vars=[4, 6], mode="both",
            show_years=[2, 5], plot_type="all_plots",
            plot_combinations=True, show_subplots=True,
            save_plots=True,
            image_path_png=str(png_dir),
            image_path_svg=str(svg_dir),
            image_prefix="test",
        )
        assert any(png_dir.iterdir())
        assert any(svg_dir.iterdir())

    def test_invalid_bbox_inches_raises(self):
        df = self._df()
        with pytest.raises(ValueError, match="bbox_inches"):
            plot_kfre_metrics(
                df, num_vars=4, show_years=2,
                bbox_inches=123,
            )
