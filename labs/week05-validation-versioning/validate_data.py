import great_expectations as gx
import pandas as pd

EXPECTED_COLUMNS = [
    "age", "annual_income", "months_employed", "loan_amount",
    "account_balance", "employment_type", "home_ownership", "defaulted",
]


def build_suite():
    suite = gx.ExpectationSuite(name="loan_applications_suite")
    expectations = [
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=EXPECTED_COLUMNS, exact_match=True),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="age", min_value=18, max_value=100),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="annual_income", min_value=12_000, max_value=1_000_000),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="age"),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="employment_type",
            value_set=["salaried", "self_employed", "unemployed"]),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="home_ownership",
            value_set=["own", "mortgage", "rent"]),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="defaulted", value_set=[0, 1]),
    ]
    for e in expectations:
        suite.add_expectation(e)
    return suite


def validate(df: pd.DataFrame) -> bool:
    context = gx.get_context(mode="ephemeral")
    source = context.data_sources.add_pandas("pandas_source")
    asset = source.add_dataframe_asset(name="loan_applications")
    batch_def = asset.add_batch_definition_whole_dataframe("batch_def")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})
    result = batch.validate(build_suite(), result_format="SUMMARY")
    if not result.success:
        print("\n DATA VALIDATION FAILED\n")
        for r in result.results:
            if not r.success:
                col = r.expectation_config.kwargs.get("column", "(table)")
                print(f" - {r.expectation_config.type} "
                      f"failed on column '{col}'")
    return result.success


if __name__ == "__main__":
    import sys
    df = pd.read_csv(sys.argv[1])
    ok = validate(df)
    sys.exit(0 if ok else 1)
