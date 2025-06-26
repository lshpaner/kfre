import pandas as pd
from kfre import eval_kfre_metrics


def test_eval_kfre_metrics_minimal():
    # build a dummy DataFrame with risk + outcome for 4-var 2-year
    df = pd.DataFrame(
        {
            "kfre_4_var_2_year": [0.1, 0.9, 0.2],
            "4_var_2_year_outcome": [0, 1, 1],
        }
    )
    metrics = eval_kfre_metrics(
        df=df,
        n_var_list=[4],
        outcome_years=[2],
    )
    # should get one row (4 vars × 2 yr)
    assert isinstance(metrics, pd.DataFrame)
    assert metrics.shape[0] == 1
    # expect at least AUC and brier_score columns
    assert "auc" in metrics.columns
    assert "brier_score" in metrics.columns
