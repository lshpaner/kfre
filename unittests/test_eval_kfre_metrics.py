import pandas as pd
from kfre import eval_kfre_metrics


def test_eval_kfre_metrics_minimal():
    # build a dummy DataFrame with risk + outcome for 4-var 2-year
    df = pd.DataFrame(
        {
            "kfre_4var_2year": [0.1, 0.9, 0.2],
            "2_year_outcome": [0, 1, 1],
        }
    )

    metrics = eval_kfre_metrics(
        df=df,
        n_var_list=[4],
        outcome_years=[2],
    )

    # Should return a DataFrame with one column for the 2-year 4-var KFRE
    assert isinstance(metrics, pd.DataFrame)
    assert list(metrics.columns) == ["2_year_4_var_kfre"]

    # The DataFrame’s index holds the metric names
    idx = metrics.index
    assert "AUC ROC" in idx
    assert "Brier Score" in idx
