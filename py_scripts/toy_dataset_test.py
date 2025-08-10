import numpy as np
import pandas as pd

# This script tests the KFRE risk prediction functionality in Python
from kfre import RiskPredictor, add_kfre_risk_col

# Create a toy dataset identical to the one used in R
toy = pd.DataFrame(
    {
        "age": [55, 72],
        "sex_txt": ["male", "female"],
        "eGFR": [45, 28],
        "uACR": [120, 800],
        "dm": [1, 0],
        "htn": [1, 1],
        "albumin": [4.2, 3.4],
        "phosphorous": [3.3, 4.6],
        "bicarbonate": [24, 22],
        "calcium": [9.1, 9.8],
    }
)

cols = dict(
    age="age",
    sex="sex_txt",
    eGFR="eGFR",
    uACR="uACR",
    dm="dm",
    htn="htn",
    albumin="albumin",
    phosphorous="phosphorous",
    bicarbonate="bicarbonate",
    calcium="calcium",
)

rp = RiskPredictor(df=toy, columns=cols)

# Match the R calls
p4 = rp.predict_kfre(
    years=2,
    is_north_american=True,
    use_extra_vars=False,
    num_vars=4,
    precision=10,
)
p6 = rp.predict_kfre(
    years=5,
    is_north_american=True,
    use_extra_vars=True,
    num_vars=6,
    precision=11,
)
p8 = rp.predict_kfre(
    years=2,
    is_north_american=True,
    use_extra_vars=True,
    num_vars=8,
    precision=10,
)

# Print results as plain lists
to_list = lambda x: x.values.tolist() if hasattr(x, "values") else list(x)
print("p4:", to_list(p4))
print("p6:", to_list(p6))
print("p8:", to_list(p8))


# ----------------------------
# kfre_person tests (row 0 and row 1), compare to vectorized outputs
# Note: kfre_person returns unrounded numerics. We compare with tolerances.
# ----------------------------
def fmt(vals, n=10):
    return [f"{v:.{n}f}" for v in vals]


# Row 0 inputs
p0_4 = rp.kfre_person(
    age=toy.loc[0, "age"],
    is_male=True,
    eGFR=toy.loc[0, "eGFR"],
    uACR=toy.loc[0, "uACR"],
    is_north_american=True,
    years=2,
)
p0_6 = rp.kfre_person(
    age=toy.loc[0, "age"],
    is_male=True,
    eGFR=toy.loc[0, "eGFR"],
    uACR=toy.loc[0, "uACR"],
    is_north_american=True,
    years=5,
    dm=toy.loc[0, "dm"],
    htn=toy.loc[0, "htn"],
)
p0_8 = rp.kfre_person(
    age=toy.loc[0, "age"],
    is_male=True,
    eGFR=toy.loc[0, "eGFR"],
    uACR=toy.loc[0, "uACR"],
    is_north_american=True,
    years=2,
    albumin=toy.loc[0, "albumin"],
    phosphorous=toy.loc[0, "phosphorous"],
    bicarbonate=toy.loc[0, "bicarbonate"],
    calcium=toy.loc[0, "calcium"],
)

# Row 1 inputs
p1_4 = rp.kfre_person(
    age=toy.loc[1, "age"],
    is_male=False,
    eGFR=toy.loc[1, "eGFR"],
    uACR=toy.loc[1, "uACR"],
    is_north_american=True,
    years=2,
)
p1_6 = rp.kfre_person(
    age=toy.loc[1, "age"],
    is_male=False,
    eGFR=toy.loc[1, "eGFR"],
    uACR=toy.loc[1, "uACR"],
    is_north_american=True,
    years=5,
    dm=toy.loc[1, "dm"],
    htn=toy.loc[1, "htn"],
)
p1_8 = rp.kfre_person(
    age=toy.loc[1, "age"],
    is_male=False,
    eGFR=toy.loc[1, "eGFR"],
    uACR=toy.loc[1, "uACR"],
    is_north_american=True,
    years=2,
    albumin=toy.loc[1, "albumin"],
    phosphorous=toy.loc[1, "phosphorous"],
    bicarbonate=toy.loc[1, "bicarbonate"],
    calcium=toy.loc[1, "calcium"],
)

print("kfre_person row0 4-var:", fmt([p0_4], 10))
print("kfre_person row0 6-var:", fmt([p0_6], 10))
print("kfre_person row0 8-var:", fmt([p0_8], 10))
print("kfre_person row1 4-var:", fmt([p1_4], 10))
print("kfre_person row1 6-var:", fmt([p1_6], 10))
print("kfre_person row1 8-var:", fmt([p1_8], 10))

# Assert kfre_person matches vectorized outputs within tolerance
# p4 has precision=10, p6 precision=11, p8 precision=10
assert np.allclose(p0_4, p4.iloc[0], atol=5e-10)
assert np.allclose(p1_4, p4.iloc[1], atol=5e-10)
assert np.allclose(p0_6, p6.iloc[0], atol=5e-11)
assert np.allclose(p1_6, p6.iloc[1], atol=5e-11)
assert np.allclose(p0_8, p8.iloc[0], atol=5e-10)
assert np.allclose(p1_8, p8.iloc[1], atol=5e-10)

# Optional: add the KFRE columns like you will in R
toy_kfre = add_kfre_risk_col(
    df=toy,
    age_col="age",
    sex_col="sex_txt",
    eGFR_col="eGFR",
    uACR_col="uACR",
    dm_col="dm",
    htn_col="htn",
    albumin_col="albumin",
    phosphorous_col="phosphorous",
    bicarbonate_col="bicarbonate",
    calcium_col="calcium",
    num_vars=[4, 6, 8],
    years=[2, 5],
    is_north_american=True,
    copy=True,
    precision=20,
)
print("new columns:", [c for c in toy_kfre.columns if c.startswith("kfre_")])
print(toy_kfre)

toy_kfre.to_csv("./data/toy_kfre.csv", index=False)

# Optional: assert against the numbers you saw in R
expected_p4 = np.array([0.01247073, 0.09997874])
expected_p6 = np.array([0.03683839, 0.30356514])  # keep your targets as-is
expected_p8 = np.array([0.01126961, 0.11930161])
assert np.allclose(np.array(p4), expected_p4, rtol=0, atol=1e-4)
assert np.allclose(np.array(p6), expected_p6, rtol=0, atol=1e-4)
assert np.allclose(np.array(p8), expected_p8, rtol=0, atol=1e-4)

print("Assertions passed, Python matches R.")
