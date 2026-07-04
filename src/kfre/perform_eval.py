"""
KFRE performance evaluation plotting.

The save and per-curve drawing utilities live in `_plot_utils.py`. This
module is the public surface and stays focused on argument validation,
prediction assembly, and plot orchestration.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_score,
    average_precision_score,
    recall_score,
    roc_auc_score,
    brier_score_loss,
    precision_score,
)

from ._plot_utils import (
    save_plot_images,
    draw_roc,
    draw_pr,
    finalize_roc_axes,
    finalize_pr_axes,
)

################################################################################
################################ ESRD Outcome ##################################
################################################################################


def class_esrd_outcome(
    df,
    col,
    years,
    duration_col,
    prefix=None,
    create_years_col=True,
    censor_incomplete=False,
):
    """Label a kidney-failure outcome within a given time horizon.

    This function does not derive the kidney-failure event itself; it applies a
    time window to a user-supplied event indicator (`col`), labeling the outcome
    as 1 when the event occurred within `years` years and 0 otherwise. It is a
    convenience utility for preparing binary outcome labels for KFRE evaluation,
    not a survival-analysis routine.

    Parameters:
    df (pd.DataFrame): DataFrame to perform calculations on.
    col (str): Column name of a binary indicator of the kidney-failure event as
    KFRE defines it, i.e. initiation of maintenance dialysis or kidney
    transplantation (kidney replacement therapy / ESKD). This is supplied by the
    user; the function does not infer the event from eGFR or any other lab value.
    years (int): The number of years to use in the condition.
    duration_col (str): The name of the column containing the duration data
    (follow-up time to event or censoring).
    prefix (str, optional): Custom prefix for the new column name.
    If None, no prefix is added.
    create_years_col (bool, optional): Whether to create the 'years' column.
    Default is True.
    censor_incomplete (bool, optional): If True, patients with no event whose
    follow-up is shorter than `years` are labeled NaN (censored) rather than 0,
    so they can be excluded from fixed-horizon evaluation. Default is False,
    which preserves the naive labeling (all non-events -> 0).

    Returns:
    pd.DataFrame: DataFrame with the new binary outcome column added.

    Notes:
    This is a naive fixed-horizon labeling: with the default
    ``censor_incomplete=False``, a value of 0 means "no event observed within
    `years` years" and therefore includes patients who were censored before the
    horizon (e.g. death without kidney failure, or loss to follow-up). It does
    not account for the competing risk of death or for right-censoring, and so
    is not a substitute for time-to-event survival analysis. In cohorts with
    substantial early mortality, treating all non-events as event-free can bias
    performance estimates; users requiring unbiased estimates should apply
    survival methods (e.g. cause-specific or subdistribution hazard models) that
    handle censoring and competing risks explicitly. Setting
    ``censor_incomplete=True`` provides a basic guard by excluding (NaN)
    non-event patients whose observed follow-up does not reach the horizon.
    """
    if create_years_col:
        # Create a 'years' column based on the duration_col
        years_col = "ESRD_duration_years"
        df[years_col] = df[duration_col] / 365.25

    else:
        # Use the provided duration_col directly
        years_col = duration_col

    if prefix is None:
        column_name = f"{years}_year_outcome"
    else:
        column_name = f"{prefix}_{years}_year_outcome"

    # Remove the column if it already exists
    if column_name in df.columns:
        df.drop(columns=[column_name], inplace=True)

    # Event within the horizon -> 1; otherwise 0.
    outcome = np.where((df[col] == 1) & (df[years_col] <= years), 1, 0).astype(float)

    if censor_incomplete:
        # A non-event patient whose follow-up ends before the horizon is
        # censored, not a confirmed non-event: label NaN so they can be
        # excluded from fixed-horizon evaluation.
        censored = (df[col] != 1) & (df[years_col] < years)
        outcome[censored.to_numpy()] = np.nan

    df[column_name] = outcome
    return df


################################################################################
######################### CKD Stage Classification #############################
################################################################################


def class_ckd_stages(
    df,
    egfr_col="eGFR",
    stage_col=None,
    combined_stage_col=None,
):
    """
    Classifies CKD stages based on eGFR values in a specified column of a DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing eGFR values.
    egfr_col (str): Name of the column in df containing eGFR values. Default is 'eGFR'.
    stage_col (str): Name of the new column to be created for CKD stage.
    combined_stage_col (str): Name of the new column to be created for combined
    CKD stage.

    Returns:
    pd.DataFrame: DataFrame with new columns containing CKD stages.
    """

    if stage_col:
        # Define the conditions for each CKD stage according to eGFR values
        conditions = [
            (df[egfr_col] >= 90),  # Condition for Stage 1
            (df[egfr_col] >= 60) & (df[egfr_col] < 90),  # Condition for Stage 2
            (df[egfr_col] >= 45) & (df[egfr_col] < 60),  # Condition for Stage 3a
            (df[egfr_col] >= 30) & (df[egfr_col] < 45),  # Condition for Stage 3b
            (df[egfr_col] >= 15) & (df[egfr_col] < 30),  # Condition for Stage 4
            (df[egfr_col] < 15),  # Condition for Stage 5
        ]

        # Define the stage names that correspond to each condition
        choices = [
            "CKD Stage 1",
            "CKD Stage 2",
            "CKD Stage 3a",
            "CKD Stage 3b",
            "CKD Stage 4",
            "CKD Stage 5",
        ]

        # Create a new column in the DataFrame
        df[stage_col] = np.select(conditions, choices, default="Not Classified")

    if combined_stage_col:
        # Combine conditions for CKD stages 3, 4, and 5 according to eGFR values
        combined_conditions = df[egfr_col] < 60

        # Define the stage names that correspond to the combined condition
        combined_choices = ["CKD Stage 3 - 5"]

        # Create a new column in the DataFrame
        df[combined_stage_col] = np.select(
            [combined_conditions], combined_choices, default="Not Classified"
        )

    return df


################################################################################
######################## Calculate Performance Metrics #########################
################################################################################


def plot_kfre_metrics(
    df,
    num_vars,
    figsize=(12, 6),
    mode="both",
    image_path_png=None,
    image_path_svg=None,
    image_filename=None,
    image_prefix=None,
    bbox_inches="tight",
    plot_type="all_plots",
    save_plots=False,
    show_years=[2, 5],
    plot_combinations=False,
    show_subplots=False,
    decimal_places=2,
    dpi=None,
):
    """
    Generate true labels and predicted probabilities for 2-year and 5-year
    outcomes, and optionally plot/save ROC and Precision-Recall curves.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the required truth and prediction columns.
    num_vars : int, list of int, or tuple of int
        Number of variables (e.g., 4) or a list/tuple (e.g., [4, 6]) to
        generate predictions for.
    figsize : tuple of int, optional
        Figure size. Default (12, 6).
    mode : {'prep', 'plot', 'both'}, optional
        'prep' returns prepared metrics only.
        'plot' plots from pre-prepped metrics.
        'both' prepares and plots. Default 'both'.
    image_path_png : str, optional
        Directory for PNG output.
    image_path_svg : str, optional
        Directory for SVG output.
    image_filename : str, optional
        Custom filename (no extension). When provided, saving is triggered
        regardless of `save_plots`. For multi-output cases (combinations,
        subplots, multi-var), a distinguishing suffix is appended.
    image_prefix : str, optional
        Prefix prepended to auto-generated filenames. Ignored when
        `image_filename` is provided.
    bbox_inches : str, optional
        Bounding box for saved images. Default 'tight'.
    plot_type : {'auc_roc', 'precision_recall', 'all_plots'}, optional
        Type of plot to generate. Default 'all_plots'.
    save_plots : bool, optional
        Whether to save plots using auto-generated filenames. Default False.
    show_years : int, list of int, or tuple of int, optional
        Year outcomes to show. Allowed values: 2 and 5. Default [2, 5].
    plot_combinations : bool, optional
        Whether to plot all variable combinations on a single set of axes.
        Default False.
    show_subplots : bool, optional
        Whether to combine all figures into a grid of subplots.
        Default False.
    decimal_places : int, optional
        Decimal places for AUC/AP scores in legends. Default 2.
    dpi : int, optional
        DPI for PNG output. Default None (matplotlib default).

    Returns
    -------
    tuple, optional
        When mode is 'prep' or 'both', returns `(y_true, preds, outcomes)`.
    """

    def format_list_or_tuple(items):
        return ", ".join(map(str, items))

    # ------------------------------------------------------------------
    # Argument validation
    # ------------------------------------------------------------------
    valid_years = [2, 5]
    if isinstance(show_years, int):
        show_years = [show_years]
    elif isinstance(show_years, tuple):
        show_years = list(show_years)
    if any(year not in valid_years for year in show_years):
        raise ValueError(
            f"The 'show_years' parameter must be a list or tuple containing "
            f"any of {valid_years}."
        )

    if isinstance(num_vars, int):
        num_vars = [num_vars]
    elif isinstance(num_vars, tuple):
        num_vars = list(num_vars)

    valid_plot_types = ["auc_roc", "precision_recall", "all_plots"]
    if plot_type not in valid_plot_types:
        raise ValueError(
            f"The 'plot_type' parameter must be one of {valid_plot_types}. "
            f"Provided: {plot_type}"
        )

    if save_plots and not (image_path_png or image_path_svg):
        raise ValueError(
            "To save plots, 'image_path_png' or 'image_path_svg' must be specified."
        )

    if not isinstance(bbox_inches, (str, type(None))):
        raise ValueError("The 'bbox_inches' parameter must be a string or None.")

    # Check required KFRE probability columns
    missing_columns = []
    for year in show_years:
        for n in num_vars:
            required_col = f"kfre_{n}var_{year}year"
            if required_col not in df.columns:
                missing_columns.append(required_col)
    if missing_columns:
        raise ValueError(
            "Must derive KFRE probabilities before generating performance "
            "evaluation metrics. "
            f"Missing columns: {', '.join(missing_columns)}"
        )

    # ------------------------------------------------------------------
    # Build truth/prediction collections
    # ------------------------------------------------------------------
    y_true = []
    outcomes = []
    for year in show_years:
        outcome_cols = df.filter(regex=f".*{year}_year_outcome").columns
        if outcome_cols.empty:
            raise ValueError(
                f"No outcome columns found matching pattern for {year}-year outcomes."
            )
        y_true.append(df[outcome_cols[0]])
        outcomes.append(f"{year}-year")

    preds = {}
    for n in num_vars:
        preds[f"{n}var"] = [df[f"kfre_{n}var_{year}year"] for year in show_years]

    result = (y_true, preds, outcomes)
    if mode == "prep":
        return result

    # ------------------------------------------------------------------
    # Filename resolution helpers
    # ------------------------------------------------------------------
    def _auto_name(suffix):
        """Auto-generated filename with optional image_prefix."""
        return f"{image_prefix}_{suffix}" if image_prefix else suffix

    def _save(auto_suffix, multi_suffix=None, fig=None):
        """
        Resolve filename and call save_plot_images.

        - When `image_filename` is set and `multi_suffix` is given (multi-output
          mode), the suffix is appended to image_filename so files don't collide.
        - When `image_filename` is set without `multi_suffix`, image_filename
          is used verbatim.
        """
        if image_filename and multi_suffix:
            effective_override = f"{image_filename}_{multi_suffix}"
        else:
            effective_override = image_filename
        save_plot_images(
            filename=_auto_name(auto_suffix),
            save_plots=save_plots,
            image_path_png=image_path_png,
            image_path_svg=image_path_svg,
            image_filename=effective_override,
            fig=fig,
            bbox_inches=bbox_inches,
            dpi=dpi,
        )

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    roc_figs, pr_figs = [], []

    if mode not in ["plot", "both"]:
        return result if mode == "both" else None

    # Multi-output flag: True when one call produces >1 distinct file.
    multi_output = (
        (plot_combinations and plot_type == "all_plots")
        or show_subplots
        or (len(num_vars) > 1 and not plot_combinations)
    )

    if plot_combinations:
        # ---- All variables overlaid on the same axes ----
        if plot_type in ["auc_roc", "all_plots"]:
            fig, ax = plt.subplots(figsize=figsize)
            for n in num_vars:
                draw_roc(
                    ax,
                    y_true,
                    preds[f"{n}var"],
                    outcomes,
                    var_label=f"{n}-variable",
                    decimal_places=decimal_places,
                )
            finalize_roc_axes(
                ax,
                f"AUC ROC: {format_list_or_tuple(num_vars)} Variable KFRE",
            )
            if not show_subplots:
                _save(
                    auto_suffix="auc_roc_curve_combined",
                    multi_suffix="auc_roc_combined" if multi_output else None,
                    fig=fig,
                )
            roc_figs.append(fig)
            if not show_subplots:
                plt.show()
            else:
                plt.close(fig)

        if plot_type in ["precision_recall", "all_plots"]:
            fig, ax = plt.subplots(figsize=figsize)
            for n in num_vars:
                draw_pr(
                    ax,
                    y_true,
                    preds[f"{n}var"],
                    outcomes,
                    var_label=f"{n}-variable",
                    decimal_places=decimal_places,
                )
            finalize_pr_axes(
                ax,
                f"Precision-Recall: {format_list_or_tuple(num_vars)} Variable KFRE",
            )
            if not show_subplots:
                _save(
                    auto_suffix="pr_curve_combined",
                    multi_suffix="pr_combined" if multi_output else None,
                    fig=fig,
                )
            pr_figs.append(fig)
            if not show_subplots:
                plt.show()
            else:
                plt.close(fig)

    else:
        # ---- One figure per variable count ----
        for n in num_vars:
            pred_list = preds[f"{n}var"]

            if plot_type in ["auc_roc", "all_plots"]:
                fig, ax = plt.subplots(figsize=figsize)
                draw_roc(
                    ax,
                    y_true,
                    pred_list,
                    outcomes,
                    var_label=f"{n}-variable",
                    decimal_places=decimal_places,
                )
                finalize_roc_axes(ax, f"AUC ROC: {n} Variable KFRE")
                if not show_subplots:
                    _save(
                        auto_suffix=f"{n}var_auc_roc",
                        multi_suffix=(f"{n}var_auc_roc" if multi_output else None),
                        fig=fig,
                    )
                roc_figs.append(fig)
                if not show_subplots:
                    plt.show()
                else:
                    plt.close(fig)

            if plot_type in ["precision_recall", "all_plots"]:
                fig, ax = plt.subplots(figsize=figsize)
                draw_pr(
                    ax,
                    y_true,
                    pred_list,
                    outcomes,
                    var_label=f"{n}-variable",
                    decimal_places=decimal_places,
                )
                finalize_pr_axes(ax, f"Precision-Recall: {n} Variable KFRE")
                if not show_subplots:
                    _save(
                        auto_suffix=f"{n}var_precision_recall",
                        multi_suffix=(
                            f"{n}var_precision_recall" if multi_output else None
                        ),
                        fig=fig,
                    )
                pr_figs.append(fig)
                if not show_subplots:
                    plt.show()
                else:
                    plt.close(fig)

    # ------------------------------------------------------------------
    # Subplots grid (preserves the original line-replay approach)
    # ------------------------------------------------------------------
    if show_subplots:
        subplot_figs = []
        if plot_type in ["auc_roc", "all_plots"]:
            subplot_figs += roc_figs
        if plot_type in ["precision_recall", "all_plots"]:
            subplot_figs += pr_figs

        if subplot_figs:
            subplot_cols = min(len(subplot_figs), 3)
            subplot_rows = (len(subplot_figs) + subplot_cols - 1) // subplot_cols
            fig, axs = plt.subplots(
                subplot_rows,
                subplot_cols,
                figsize=(figsize[0] * subplot_cols, figsize[1] * subplot_rows),
            )

            if subplot_rows == 1 and subplot_cols == 1:
                axs = np.array([axs])
            elif subplot_rows == 1 or subplot_cols == 1:
                axs = np.expand_dims(axs, axis=0 if subplot_rows == 1 else 1)

            axs = axs.flatten()
            for ax, fig_ in zip(axs, subplot_figs):
                fig_.axes[0].get_figure().sca(fig_.axes[0])
                for line in fig_.axes[0].get_lines():
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    if (
                        len(xdata) != 2
                        or len(ydata) != 2
                        or not ((xdata == [0, 1]).all() and (ydata == [0, 1]).all())
                    ):
                        ax.plot(xdata, ydata, label=line.get_label())
                if "roc" in fig_.axes[0].get_title().lower():
                    ax.plot([0, 1], [0, 1], linestyle="--")
                ax.legend(loc="best")
                ax.set_title(fig_.axes[0].get_title())
                ax.set_xlabel(fig_.axes[0].get_xlabel())
                ax.set_ylabel(fig_.axes[0].get_ylabel())
            for ax in axs[len(subplot_figs) :]:
                fig.delaxes(ax)
            plt.tight_layout()

            if plot_type == "all_plots" and plot_combinations:
                auto_suffix = "subplot_all_plots_combination"
            elif image_prefix:
                auto_suffix = "subplot"
            else:
                auto_suffix = "performance_subplot"

            _save(
                auto_suffix=auto_suffix,
                multi_suffix="subplot",
                fig=fig,
            )
            plt.show()

    if mode == "both":
        return result
    return None


################################################################################
######################## Calculate Performance Metrics #########################
################################################################################


def eval_kfre_metrics(
    df,
    n_var_list,
    outcome_years=2,
    decimal_places=6,
):
    """
    Calculate metrics for multiple outcomes and store the results in a DataFrame.

    This function computes a set of performance metrics for multiple binary
    classification models given the true labels and the predicted probabilities
    for each outcome. The metrics calculated include precision
    (positive predictive value), average precision, sensitivity (recall),
    specificity, AUC ROC, and Brier score.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing the necessary columns for truth and
        predictions.
    n_var_list : list of int
        List of variable numbers to consider, e.g., [4, 6, 8].
    outcome_years : list, tuple, or int, optional
        List, tuple, or single year to consider for outcomes, default is [2].
    decimal_places : int, optional
        Number of decimal places for the calculated metrics. Default is 6.

    Returns:
    -------
    pd.DataFrame
        A DataFrame containing the calculated metrics for each outcome.

    Notes:
    -----
    - Precision is calculated with a threshold of 0.5 for the predicted
      probabilities.
    - Sensitivity is also known as recall.
    - Specificity is calculated as the recall for the negative class.
    - AUC ROC is calculated using the receiver operating characteristic curve.
    - Brier score measures the mean squared difference between predicted
      probabilities and the true binary outcomes.
    """

    # Ensure outcome_years is a list
    if isinstance(outcome_years, int):
        outcome_years = [outcome_years]
    elif isinstance(outcome_years, tuple):
        outcome_years = list(outcome_years)

    # Validate n_var_list
    valid_vars = [4, 6, 8]  # Define valid variable numbers
    if any(n_var not in valid_vars for n_var in n_var_list):
        raise ValueError(
            "Invalid variable number in n_var_list. Valid options are either "
            "4, 6, 8, or combination of any (or all) of these in a list or tuple."
        )

    # Validate outcome_years
    valid_outcome_years = [2, 5]
    if any(year not in valid_outcome_years for year in outcome_years):
        raise ValueError(
            "Invalid value for year in outcome_years. Valid options are 2, 5, "
            "or both as a list or tuple."
        )

    # Extract the true labels for the outcomes using regex
    y_true = []
    outcomes = []
    for year in outcome_years:
        outcome_col = df.filter(regex=f".*{year}_year_outcome").columns
        if not outcome_col.empty:
            y_true.append(df[outcome_col[0]])
            outcomes.append(f"{year}_year")
        else:
            raise ValueError(f"{year}_year_outcome must exist to derive these metrics.")

    # Initialize a dictionary to store the predicted probabilities for each
    # number of variables
    preds_n_var_dict = {}

    # Iterate over each number of variables specified in n_var_list
    for n_var in n_var_list:
        # Initialize an empty list for storing predictions corresponding to this
        # number of variables
        preds_n_var_dict[n_var] = []

        # Iterate over each outcome
        for year in outcome_years:
            # Construct the column name for the predicted probabilities
            col_name = f"kfre_{n_var}var_{year}year"
            if col_name in df.columns:
                preds_n_var_dict[n_var].append(df[col_name])
            else:
                preds_n_var_dict[n_var].append(None)

    # Initialize an empty list to store the calculated metrics for each
    # combination of variables and outcomes
    metrics_list_n_var = []

    # Iterate over each number of variables and its corresponding predictions
    for n_var, preds in preds_n_var_dict.items():
        # Iterate over each outcome, true labels, and predicted labels
        for outcome, true_labels, pred_labels in zip(outcomes, y_true, preds):
            # Only calculate metrics if the predicted labels are not None
            if pred_labels is not None:
                # Calculate precision (positive predictive value)
                precision = precision_score(true_labels, pred_labels > 0.5)
                # Calculate sensitivity (recall)
                sensitivity = recall_score(true_labels, pred_labels > 0.5)
                # Calculate specificity (recall for the negative class)
                specificity = recall_score(
                    true_labels,
                    pred_labels > 0.5,
                    pos_label=0,
                )
                # Calculate AUC ROC (Area Under the Receiver Operating
                # Characteristic curve)
                auc_roc = roc_auc_score(true_labels, pred_labels)
                # Calculate Brier score (mean squared difference between
                # predicted probabilities and true binary outcomes)
                brier = brier_score_loss(true_labels, pred_labels)
                # Calculate average precision (area under the precision-recall curve)
                average_precision = average_precision_score(
                    true_labels,
                    pred_labels,
                )

                # Create a dictionary to store the calculated metrics
                metrics = {
                    "Precision/PPV": round(precision, decimal_places),
                    "Average Precision": round(average_precision, decimal_places),
                    "Sensitivity": round(sensitivity, decimal_places),
                    "Specificity": round(specificity, decimal_places),
                    "AUC ROC": round(auc_roc, decimal_places),
                    "Brier Score": round(brier, decimal_places),
                    "Outcome": f"{outcome}_{n_var}_var_kfre",
                }

                # Append the dictionary to the metrics list
                metrics_list_n_var.append(metrics)

    # Convert the list of metrics dictionaries to a DataFrame
    metrics_df_n_var = pd.DataFrame(metrics_list_n_var)

    # Set the 'Outcome' column as the index and transpose the DataFrame for
    # better readability
    metrics_df_n_var = metrics_df_n_var.set_index("Outcome").T

    # Rename the axis to 'Metrics' for clarity
    metrics_df_n_var = metrics_df_n_var.rename_axis("Metrics")

    # Return the resulting DataFrame containing the performance metrics
    return metrics_df_n_var


################################################################################
############################ Bootstrap Metric CI ###############################
################################################################################


def bootstrap_metric_ci(
    y_true,
    y_score,
    metric="auc_roc",
    n_boot=1000,
    ci=95,
    threshold=0.5,
    seed=None,
    progress=True,
):
    """
    Estimate a bootstrap confidence interval for a performance metric.

    Resamples patients with replacement ``n_boot`` times, recomputes the metric
    on each resample, and returns the point estimate together with the lower and
    upper percentile bounds of the requested confidence level. Resamples in which
    the metric is undefined (e.g. only one outcome class present, which makes
    AUC ROC / average precision undefined) are skipped.

    Parameters:
    - y_true (array-like): Binary ground-truth labels (0/1). NaNs are dropped
      pairwise with y_score before resampling.
    - y_score (array-like): Predicted risk scores (probabilities in [0, 1]).
    - metric (str): One of "precision", "average_precision", "sensitivity",
      "specificity", "auc_roc", "brier". Threshold-based metrics (precision,
      sensitivity, specificity) use ``threshold`` to binarize y_score.
    - n_boot (int): Number of bootstrap resamples. Default 1000.
    - ci (float): Confidence level as a percentage (e.g. 95). Default 95.
    - threshold (float): Cutoff for threshold-based metrics. Default 0.5.
    - seed (int, optional): Seed for reproducibility.

    Returns:
    - dict: {"metric": str, "point": float, "lower": float, "upper": float,
             "ci": float, "n_boot_valid": int} where point is the metric on the
      full sample and lower/upper are the CI bounds. Values are NaN if the metric
      cannot be computed on the full sample.
    """
    import numpy as np
    from sklearn.metrics import (
        precision_score,
        recall_score,
        roc_auc_score,
        average_precision_score,
        brier_score_loss,
    )

    def _compute(yt, ys):
        # Returns the metric value or np.nan if undefined for this sample.
        classes = np.unique(yt)
        if metric == "brier":
            return brier_score_loss(yt, ys)
        if metric in ("auc_roc", "average_precision"):
            if classes.size < 2:
                return np.nan
            if metric == "auc_roc":
                return roc_auc_score(yt, ys)
            return average_precision_score(yt, ys)
        # Threshold-based metrics
        yp = (ys > threshold).astype(int)
        if metric == "precision":
            return precision_score(yt, yp, zero_division=0)
        if metric == "sensitivity":
            return recall_score(yt, yp, zero_division=0)
        if metric == "specificity":
            return recall_score(yt, yp, pos_label=0, zero_division=0)
        raise ValueError(
            f"Unknown metric {metric!r}. Choose from: precision, "
            "average_precision, sensitivity, specificity, auc_roc, brier."
        )

    y_true = np.asarray(y_true, dtype=float)
    y_score = np.asarray(y_score, dtype=float)

    # Drop pairs with NaN in either array (e.g. censored outcomes).
    keep = ~(np.isnan(y_true) | np.isnan(y_score))
    y_true = y_true[keep].astype(int)
    y_score = y_score[keep]

    point = _compute(y_true, y_score) if y_true.size else np.nan

    rng = np.random.default_rng(seed)
    n = y_true.size
    boot_vals = []

    # Single progress bar over all resamples for this call.
    iterator = range(n_boot)
    if progress:
        try:
            from tqdm import tqdm

            iterator = tqdm(iterator, total=n_boot, desc=f"Bootstrapping {metric}")
        except ImportError:
            print("tqdm not installed; proceeding without a progress bar.")

    for _ in iterator:
        idx = rng.integers(0, n, size=n)
        val = _compute(y_true[idx], y_score[idx])
        if not np.isnan(val):
            boot_vals.append(val)

    if boot_vals:
        alpha = (100 - ci) / 2
        lower = float(np.percentile(boot_vals, alpha))
        upper = float(np.percentile(boot_vals, 100 - alpha))
    else:
        lower = upper = np.nan

    return {
        "metric": metric,
        "point": float(point) if not np.isnan(point) else np.nan,
        "lower": lower,
        "upper": upper,
        "ci": float(ci),
        "n_boot_valid": len(boot_vals),
    }
