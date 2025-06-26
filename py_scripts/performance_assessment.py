import os
from kfre import eval_kfre_metrics
from batch_risk_calculations import df

print(df)

terminal_size = os.get_terminal_size()

metrics_df_n_var = eval_kfre_metrics(
    df=df,  # Metrics-ready DataFrame as the first argument
    n_var_list=[4, 6, 8],  # Specify the list of variable numbers to consider
    outcome_years=[2, 5],  # Specify the list of outcome years to consider
)

print("=" * terminal_size.columns)
print("\nMetrics DataFrame for 4, 6, and 8 variable models:")
print("Warning: Not very many patients in the dataset, so metrics may not be reliable.")
print("=" * terminal_size.columns)
print(f"\n{metrics_df_n_var}\n")
