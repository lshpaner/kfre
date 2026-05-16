"""
Internal plotting helpers for kfre.

Mirrors the pattern in `model_metrics.metrics_utils`: a centralized save
helper plus small per-curve drawing utilities that keep the public plotting
functions thin and free of duplicated savefig/axes-styling code.
"""

import os

import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
)


def save_plot_images(
    filename,
    save_plots,
    image_path_png,
    image_path_svg,
    image_filename=None,
    fig=None,
    bbox_inches="tight",
    dpi=None,
):
    """
    Centralized figure-saving helper. Mirrors
    `model_metrics.metrics_utils.save_plot_images`.

    Saving is triggered when either `save_plots` is True OR `image_filename`
    is provided. When `image_filename` is provided it takes precedence over
    the auto-generated `filename`.

    Parameters
    ----------
    filename : str
        Auto-generated base filename (used when `image_filename` is None).
    save_plots : bool
        Whether to save plots based on the auto-generated filename.
    image_path_png : str or None
        Directory for PNG output. If None, PNG output is skipped.
    image_path_svg : str or None
        Directory for SVG output. If None, SVG output is skipped.
    image_filename : str, optional
        Custom filename override (no extension). When provided, saving is
        triggered regardless of `save_plots`.
    fig : matplotlib.figure.Figure, optional
        Figure to save. Defaults to the current active figure.
    bbox_inches : str, optional
        `bbox_inches` argument passed to `savefig`.
    dpi : int, optional
        DPI for raster outputs (PNG only).
    """
    should_save = save_plots or (image_filename is not None)
    if not should_save:
        return
    if image_path_png is None and image_path_svg is None:
        return

    effective_name = image_filename if image_filename else filename
    if effective_name is None:
        return

    fig = fig or plt.gcf()

    if image_path_png:
        os.makedirs(image_path_png, exist_ok=True)
        fig.savefig(
            os.path.join(image_path_png, f"{effective_name}.png"),
            bbox_inches=bbox_inches,
            dpi=dpi,
        )

    if image_path_svg:
        os.makedirs(image_path_svg, exist_ok=True)
        fig.savefig(
            os.path.join(image_path_svg, f"{effective_name}.svg"),
            bbox_inches=bbox_inches,
        )


def draw_roc(ax, true_list, pred_list, outcomes, var_label, decimal_places=2):
    """Draw ROC curves for a set of (truth, prediction) pairs on a given Axes."""
    for true_labels, pred_labels, outcome in zip(true_list, pred_list, outcomes):
        fpr, tpr, _ = roc_curve(true_labels, pred_labels)
        auc_score = auc(fpr, tpr)
        ax.plot(
            fpr,
            tpr,
            label=(
                f"{var_label} {outcome} outcome "
                f"(AUC = {auc_score:.{decimal_places}f})"
            ),
        )


def draw_pr(ax, true_list, pred_list, outcomes, var_label, decimal_places=2):
    """Draw Precision-Recall curves for a set of pairs on a given Axes."""
    for true_labels, pred_labels, outcome in zip(true_list, pred_list, outcomes):
        precision, recall, _ = precision_recall_curve(true_labels, pred_labels)
        ap_score = average_precision_score(true_labels, pred_labels)
        ax.plot(
            recall,
            precision,
            label=(
                f"{var_label} {outcome} outcome "
                f"(AP = {ap_score:.{decimal_places}f})"
            ),
        )


def finalize_roc_axes(ax, title):
    """Apply standard ROC styling: diagonal, axis labels, title, legend."""
    ax.plot([0, 1], [0, 1], linestyle="--", color="red")
    ax.set_xlabel("1 - Specificity")
    ax.set_ylabel("Sensitivity")
    ax.set_title(title)
    ax.legend(loc="best")


def finalize_pr_axes(ax, title):
    """Apply standard PR styling: axis labels, title, legend."""
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title)
    ax.legend(loc="best")
