import os
import pandas as pd
from kfre import perform_conversions, upcr_uacr

terminal_size = os.get_terminal_size()

data = {
    "Age": [87.24, 56.88, 66.53, 69.92, 81.14],
    "SEX": ["Male", "Female", "Female", "Male", "Female"],
    "uPCR": [33.0, 395.0, 163.0, 250.0, 217.0],
    "Calcium (mmol/L)": [2.78, 2.43, 2.33, 2.29, 2.45],
    "Bicarbonate (mmol/L)": [27.2, 21.3, 27.8, 20.7, 26.2],
    "eGFR-EPI": [19, 15, 17, 12, 15],
    "Albumin (g/l)": [37.0, 30.0, 36.0, 39.0, 43.0],
    "Phosphate (mmol/L)": [0.88, 1.02, 1.24, 1.80, 1.39],
    "Diabetes (1=yes; 0=no)": [1, 0, 0, 0, 1],
    "Hypertension (1=yes; 0=no)": [1, 1, 1, 1, 1],
    "Follow-up YEARS": [5.7, 1.5, 0.6, 1.1, 2.5],
    "ESRD": ["", 1, "", 1, ""],
}

df = pd.DataFrame(data)


print("-" * terminal_size.columns)
print(f"\nOriginal DataFrame:\n{df}\n")

# Perform conversions using the wrapper function
converted_df = perform_conversions(
    df=df,
    reverse=False,
    convert_all=True,
)

print("-" * terminal_size.columns)
print(f"\nConverted DataFrame:\n{converted_df}\n")

# Calculate uACR
converted_df["uACR"] = upcr_uacr(
    df=converted_df,
    sex_col="SEX",
    diabetes_col="Diabetes (1=yes; 0=no)",
    hypertension_col="Hypertension (1=yes; 0=no)",
    upcr_col="uPCR_mg_g",
    female_str="Female",
)


print("-" * terminal_size.columns)
print(f"Calculated uACR:\n{converted_df['uACR']}\n")
