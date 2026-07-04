import numpy as np
import pytest
from kfre import bootstrap_metric_ci


def _data(n=400, seed=0):
    rng = np.random.default_rng(seed)
    y_true = (rng.random(n) < 0.2).astype(int)
    y_score = np.clip(0.1 + 0.5 * y_true + rng.normal(0, 0.2, n), 0, 1)
    return y_true, y_score


class TestBootstrapMetricCI:
    @pytest.mark.parametrize(
        "metric",
        [
            "auc_roc",
            "average_precision",
            "precision",
            "sensitivity",
            "specificity",
            "brier",
        ],
    )
    def test_returns_ordered_ci_for_each_metric(self, metric):
        y_true, y_score = _data()
        r = bootstrap_metric_ci(y_true, y_score, metric=metric, n_boot=200, seed=42)
        assert not np.isnan(r["point"])
        assert r["lower"] <= r["point"] <= r["upper"]
        assert r["n_boot_valid"] > 0

    def test_reproducible_with_seed(self):
        y_true, y_score = _data()
        a = bootstrap_metric_ci(y_true, y_score, "auc_roc", n_boot=200, seed=7)
        b = bootstrap_metric_ci(y_true, y_score, "auc_roc", n_boot=200, seed=7)
        assert a == b

    def test_drops_nan_outcomes(self):
        y_true, y_score = _data()
        yt = y_true.astype(float)
        yt[:30] = np.nan  # censored
        r = bootstrap_metric_ci(yt, y_score, "auc_roc", n_boot=200, seed=1)
        assert not np.isnan(r["point"])

    def test_unknown_metric_raises(self):
        y_true, y_score = _data()
        with pytest.raises(ValueError):
            bootstrap_metric_ci(y_true, y_score, metric="f1")

    def test_ci_width_shrinks_with_more_data(self):
        # Wider CI on small n than on large n (sanity check on the bootstrap).
        yt_s, ys_s = _data(n=80, seed=3)
        yt_l, ys_l = _data(n=2000, seed=3)
        w_small = (lambda r: r["upper"] - r["lower"])(
            bootstrap_metric_ci(yt_s, ys_s, "auc_roc", n_boot=300, seed=5)
        )
        w_large = (lambda r: r["upper"] - r["lower"])(
            bootstrap_metric_ci(yt_l, ys_l, "auc_roc", n_boot=300, seed=5)
        )
        assert w_large < w_small
