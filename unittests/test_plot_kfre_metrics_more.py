# unittests/test_plot_kfre_metrics_more.py

import matplotlib

matplotlib.use("Agg")  # ← Use non-GUI backend to avoid Tk errors

import pandas as pd
import matplotlib.pyplot as plt
from kfre.perform_eval import plot_kfre_metrics


def sample_df():
    # Provide both 4-var and 6-var columns so mode="prep" doesn’t error out
    return pd.DataFrame(
        {
            "kfre_4var_2year": [0.1, 0.9],
            "2_year_outcome": [0, 1],
            "kfre_4var_5year": [0.2, 0.8],
            "5_year_outcome": [1, 0],
            # Dummy 6-var predictions
            "kfre_6var_2year": [0.15, 0.85],
            "kfre_6var_5year": [0.25, 0.75],
        }
    )


def test_prep_mode_multiple_vars_and_years():
    df = sample_df()
    y_true, preds, outcomes = plot_kfre_metrics(
        df.copy(),
        num_vars=[4, 6],
        mode="prep",
        show_years=[2, 5],
        plot_type="all_plots",
    )
    # both years must be present
    assert outcomes == ["2-year", "5-year"]
    # preds should have entries for both 4var and 6var
    assert set(preds.keys()) == {"4var", "6var"}
    # each preds["Xvar"] is a list of two Series
    assert all(len(preds[key]) == 2 for key in preds)


def test_mode_plot_calls_show(monkeypatch):
    df = sample_df()
    calls = []
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: calls.append(True))
    result = plot_kfre_metrics(
        df.copy(),
        num_vars=4,
        mode="plot",
        show_years=2,
        plot_type="auc_roc",
    )
    assert result is None
    assert calls, "plt.show() should be called at least once"


def test_save_plots_and_subplots_to_disk(tmp_path, monkeypatch):
    df = sample_df()
    # silence plt.show()
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    png_dir = tmp_path / "pngs"
    svg_dir = tmp_path / "svgs"

    plot_kfre_metrics(
        df.copy(),
        num_vars=[4],
        mode="both",
        show_years=[2, 5],
        plot_combinations=True,
        show_subplots=True,
        save_plots=True,
        image_path_png=str(png_dir),
        image_path_svg=str(svg_dir),
        image_prefix="test",
    )

    # Ensure files were written out
    assert any(p.suffix == ".png" for p in png_dir.iterdir()), "No PNGs written"
    assert any(p.suffix == ".svg" for p in svg_dir.iterdir()), "No SVGs written"
