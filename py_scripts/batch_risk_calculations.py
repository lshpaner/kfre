import os
from kfre import add_kfre_risk_col, class_esrd_outcome
from conversions import converted_df
from classify_esrd_outcomes import df

terminal_size = os.get_terminal_size()
converted_df = converted_df.merge(
    df, how="inner"
)  # merge 2_year_outcome and 5_year_outcome columns into converted_df

print(f"\n{converted_df}")

df = add_kfre_risk_col(
    df=converted_df,
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
    copy=False,  # Modify the original DataFrame directly
)
# The resulting DataFrame 'df' now includes new columns with risk
# predictions for each model and time frame

print("-" * terminal_size.columns)
print(
    f"\n4-6-8 variable equation probabilities:\n\n{df[[col for col in df.columns if 'kfre_' in col]]}\n"
)
