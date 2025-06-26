from kfre import kfre_person

risk_percentage = (
    kfre_person(
        age=57.28,
        is_male=False,
        eGFR=15.0,
        uACR=1762.001840,
        is_north_american=False,
        years=2,
        dm=None,
        htn=None,
        albumin=None,
        phosphorous=None,
        bicarbonate=None,
        calcium=None,
    )
    * 100
)  # Convert to percentage

message = f"The 2-year risk of kidney failure for this patient is"
print(f"{message} {risk_percentage:.2f}%.")


for years in [2, 5]:
    risk_percentage = (
        kfre_person(
            age=57.28,
            is_male=False,  # is the patient male?
            eGFR=15.0,  # ml/min/1.73 m^2
            uACR=1762.001840,  # mg/g
            is_north_american=False,  # is the patient from North America?
            years=years,
            ################################################################
            # Uncomment "dm" and "htn" for the 6-variable model:
            ################################################################
            # dm=0,
            # htn=1,
            ################################################################
            # Comment out "dm" and "htn"; uncomment the following lines for
            # the 8-variable model:
            ################################################################
            # albumin=3.0, # g/dL
            # phosphorous=3.162, # mg/dL
            # bicarbonate=21.3, # mEq/L
            # calcium=9.72, # mg/dL
        )
        * 100  # multiply by 100 to convert to percentage
    )

    message = f"The {years}-year risk of kidney failure for this patient is"
    print(f"{message} {risk_percentage:.2f}%.")
